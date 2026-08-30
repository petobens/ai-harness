#!/usr/bin/env python3
"""Normalize Codex and Claude Code JSONL session events."""

import argparse
import json
import re
import sys
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_ROOTS = (
    Path.home() / ".codex" / "sessions",
    Path.home() / ".claude" / "projects",
)


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0


def _output_text(output: Any) -> str:
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        parts: list[str] = []
        for block in output:
            if isinstance(block, dict):
                parts.append(str(block.get("text", block.get("content", ""))))
        return "\n".join(filter(None, parts))
    return json.dumps(output, ensure_ascii=False) if output is not None else ""


def _codex_events(record: dict[str, Any]) -> Iterator[dict[str, Any]]:
    payload = record.get("payload", {})
    if not isinstance(payload, dict):
        return
    common = {"timestamp": record.get("timestamp")}
    if record.get("type") == "event_msg":
        kind = payload.get("type")
        role = (
            {"user_message": "user", "agent_message": "assistant"}.get(kind)
            if isinstance(kind, str)
            else None
        )
        if role:
            yield common | {
                "kind": "message",
                "role": role,
                "event_id": record.get("timestamp"),
                "text": str(payload.get("message", "")),
            }
        return

    if record.get("type") != "response_item":
        return
    kind = payload.get("type")
    if not isinstance(kind, str):
        return
    if kind in {"function_call", "custom_tool_call"}:
        yield common | {
            "kind": "tool_call",
            "role": "assistant",
            "event_id": payload.get("call_id", payload.get("id")),
            "name": payload.get("name"),
            "text": _output_text(payload.get("arguments", payload.get("input", ""))),
        }
    elif kind in {"function_call_output", "custom_tool_call_output"}:
        yield common | {
            "kind": "tool_result",
            "role": "tool",
            "event_id": payload.get("call_id"),
            "text": _output_text(payload.get("output")),
        }


def _claude_events(record: dict[str, Any]) -> Iterator[dict[str, Any]]:
    role = record.get("type")
    if not isinstance(role, str) or role not in {"user", "assistant"}:
        return
    message = record.get("message", {})
    if not isinstance(message, dict):
        return
    content = message.get("content")
    common = {"timestamp": record.get("timestamp")}
    if isinstance(content, str):
        yield common | {
            "kind": "message",
            "role": role,
            "event_id": record.get("uuid"),
            "text": content,
        }
        return
    if not isinstance(content, list):
        return
    for index, block in enumerate(content):
        if not isinstance(block, dict):
            continue
        kind = block.get("type")
        if kind == "text":
            yield common | {
                "kind": "message",
                "role": role,
                "event_id": (
                    f"{record['uuid']}:{index}" if record.get("uuid") else None
                ),
                "text": str(block.get("text", "")),
            }
        elif kind == "tool_use":
            yield common | {
                "kind": "tool_call",
                "role": "assistant",
                "event_id": block.get("id"),
                "name": block.get("name"),
                "text": json.dumps(block.get("input", {}), ensure_ascii=False),
            }
        elif kind == "tool_result":
            yield common | {
                "kind": "tool_result",
                "role": "tool",
                "event_id": block.get("tool_use_id"),
                "text": _output_text(block.get("content")),
            }


def _session_files(
    targets: list[str], since: datetime | None, all_sessions: bool
) -> list[Path]:
    if targets:
        files: list[Path] = []
        for target in dict.fromkeys(targets):
            path = Path(target).expanduser()
            matches = (
                [path]
                if path.is_file()
                else [
                    candidate
                    for root in DEFAULT_ROOTS
                    if root.exists()
                    for candidate in root.rglob(f"*{target}*.jsonl")
                ]
            )
            if not matches:
                raise SystemExit(f"Session not found: {target}")
            exact = [candidate for candidate in matches if target in candidate.name]
            files.extend(exact or matches)
        return sorted(dict.fromkeys(files))

    if since is None and not all_sessions:
        raise SystemExit("Provide a session ID/path or --since YYYY-MM-DD")
    cutoff = since.timestamp() if since else 0
    return sorted(
        path
        for root in DEFAULT_ROOTS
        if root.exists()
        for path in root.rglob("*.jsonl")
        if _mtime(path) >= cutoff
    )


def _records(path: Path, *, warn: bool = True) -> Iterator[dict[str, Any]]:
    try:
        with path.open(encoding="utf-8", errors="replace") as session:
            for line_number, line in enumerate(session, 1):
                try:
                    record = json.loads(line)
                    if isinstance(record, dict):
                        yield record
                    elif warn:
                        print(
                            f"warning: {path}:{line_number}: expected JSON object",
                            file=sys.stderr,
                        )
                except json.JSONDecodeError as error:
                    if warn:
                        print(
                            f"warning: {path}:{line_number}: {error}", file=sys.stderr
                        )
    except OSError as error:
        if warn:
            print(f"warning: {path}: {error}", file=sys.stderr)


def _session_info(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "agent": None,
        "session_id": None,
        "cwd": None,
        "is_subagent": False,
        "updated_at": int(_mtime(path)),
    }
    for index, record in enumerate(_records(path, warn=False)):
        if record.get("type") == "session_meta":
            payload = record.get("payload", {})
            if not isinstance(payload, dict):
                continue
            source = payload.get("source")
            info |= {
                "agent": "codex",
                "session_id": payload.get("id", payload.get("session_id")),
                "cwd": payload.get("cwd"),
                "is_subagent": bool(
                    isinstance(source, dict) and source.get("subagent")
                ),
            }
            break
        if record.get("sessionId"):
            info |= {
                "agent": "claude",
                "session_id": record.get("sessionId", path.stem),
                "cwd": record.get("cwd", info["cwd"]),
                "is_subagent": bool(record.get("isSidechain")),
            }
            if info["cwd"] is not None and record.get("isSidechain") is not None:
                break
        if index >= 499:
            break
    return info


def _print_coverage(files: list[Path]) -> None:
    coverage: dict[str, dict[str, Any]] = {}
    for path in files:
        info = _session_info(path)
        agent = info["agent"]
        if not agent:
            print(f"warning: unrecognized session format: {path}", file=sys.stderr)
            continue
        entry = coverage.setdefault(
            agent,
            {
                "agent": agent,
                "sessions": 0,
                "top_level": 0,
                "subagents": 0,
                "oldest_updated_at": None,
                "newest_updated_at": None,
            },
        )
        entry["sessions"] += 1
        entry["subagents" if info["is_subagent"] else "top_level"] += 1
        updated_at = info["updated_at"]
        if updated_at:
            oldest = entry["oldest_updated_at"]
            newest = entry["newest_updated_at"]
            entry["oldest_updated_at"] = (
                min(oldest, updated_at) if oldest else updated_at
            )
            entry["newest_updated_at"] = (
                max(newest, updated_at) if newest else updated_at
            )
    for entry in coverage.values():
        for field in ("oldest_updated_at", "newest_updated_at"):
            timestamp = entry[field]
            if timestamp:
                entry[field] = (
                    datetime.fromtimestamp(timestamp).astimezone().isoformat()
                )
        print(json.dumps(entry, ensure_ascii=False))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sessions", nargs="*", help="session IDs or JSONL paths")
    parser.add_argument(
        "--since",
        type=datetime.fromisoformat,
        metavar="DATE",
        help="sessions modified on or after this ISO date",
    )
    parser.add_argument("--cwd", dest="cwd_pattern", help="case-insensitive cwd filter")
    parser.add_argument("--grep", dest="pattern", help="case-insensitive event filter")
    parser.add_argument(
        "--messages-only", action="store_true", help="omit tool calls and results"
    )
    parser.add_argument(
        "--include-subagents",
        action="store_true",
        help="include delegated sessions in broad scans",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="report retained session counts and date ranges, then exit",
    )
    parser.add_argument(
        "--paths-only", action="store_true", help="print each matching session once"
    )
    return parser.parse_args()


def _main() -> None:
    args = _parse_args()
    pattern = re.compile(args.pattern, re.IGNORECASE) if args.pattern else None
    cwd_pattern = (
        re.compile(args.cwd_pattern, re.IGNORECASE) if args.cwd_pattern else None
    )
    files = _session_files(args.sessions, args.since, args.coverage)
    if args.coverage:
        _print_coverage(files)
        return
    seen: set[tuple[str, str, str]] = set()
    matched_paths: set[Path] = set()
    for path in files:
        info = _session_info(path)
        agent = info["agent"]
        if not agent:
            print(f"warning: unrecognized session format: {path}", file=sys.stderr)
            continue
        if not args.sessions and info["is_subagent"] and not args.include_subagents:
            continue
        if cwd_pattern and not cwd_pattern.search(info["cwd"] or ""):
            continue
        parser = _codex_events if agent == "codex" else _claude_events
        for record in _records(path):
            for event in parser(record):
                if args.messages_only and event["kind"] != "message":
                    continue
                if pattern and not pattern.search(event.get("text", "")):
                    continue
                if args.paths_only:
                    if path not in matched_paths:
                        print(path)
                        matched_paths.add(path)
                    continue
                event_id = event.get("event_id")
                if event_id:
                    key = (event["kind"], event["role"], str(event_id))
                    if key in seen:
                        continue
                    seen.add(key)
                print(
                    json.dumps(
                        {"path": str(path)} | info | event,
                        ensure_ascii=False,
                    )
                )


if __name__ == "__main__":
    _main()
