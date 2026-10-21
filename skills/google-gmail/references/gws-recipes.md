# Gmail gws recipes

## Access

Use the existing `gws` account. `gws auth status` checks local configuration;
`gws gmail users getProfile --params '{"userId":"me"}'` verifies live access
and the mailbox identity. Never print exported credentials or tokens.

Enable the Gmail API in the OAuth client's Google Cloud project if the API
returns `accessNotConfigured`; use the enable URL from the error. Missing OAuth
scopes are a separate problem. Reading bodies and searching require
`https://www.googleapis.com/auth/gmail.readonly` (or an already granted broader
scope); `gmail.metadata` cannot search with `q` or read bodies.

For a new read-only setup, `gws auth login --readonly --services gmail`
opens the consent flow. For an existing Workspace setup, preserve its required
Drive, Docs, Sheets, and Slides scopes when reauthorizing: use the scope picker
or `--scopes` with the complete desired set, adding Gmail read access. Do not
replace existing write access with a read-only service subset. Check
`gws auth login --help` for installed-version options.

## Search and read

```bash
# Search IDs first; replace the example query with the user's criteria
gws gmail users messages list --params '{"userId":"me","q":"in:inbox newer_than:7d","maxResults":50,"fields":"messages(id,threadId),nextPageToken,resultSizeEstimate"}'

# Inspect headers without loading the body
gws gmail users messages get --params '{"userId":"me","id":"MESSAGE_ID","format":"metadata","metadataHeaders":["From","To","Cc","Subject","Date","Message-ID"]}'

# Read one message's decoded plain-text body and main headers
gws gmail +read --id MESSAGE_ID --headers

# Read a complete message or conversation
gws gmail users messages get --params '{"userId":"me","id":"MESSAGE_ID","format":"full"}'
gws gmail users threads get --params '{"userId":"me","id":"THREAD_ID","format":"full"}'

# Resolve user label names to API IDs
gws gmail users labels list --params '{"userId":"me"}'
```

Pass the returned `nextPageToken` as `pageToken` with the same query for the next
page. Use `includeSpamTrash:true` only when that coverage is relevant. Useful
search operators include `from:`, `to:`, `subject:`, `has:attachment`,
`filename:`, `is:unread`, `after:`, and `before:`. Build JSON with a serializer
when interpolating user text; do not interpolate it into shell code.

For exact local date boundaries, convert the requested time zone's boundaries
to epoch seconds and use `after:EPOCH before:EPOCH`. Gmail's date-only searches
use Pacific midnight. API searches do not expand account aliases or match an
entire thread the same way the Gmail UI does; include known aliases explicitly
and retrieve matching threads for context.

For received mail, exclude sent messages and drafts rather than restricting the
search to `in:inbox`, which misses archived mail. To rank messages by receipt
time, use `internalDate` (epoch milliseconds), not the sender's `Date` header.
For an exact latest-N result, retrieve metadata for all matches in the bounded
interval and sort by `internalDate`; the list endpoint has no `orderBy` option.
For a busy mailbox, start with the end of the requested interval and expand
backward until it contains at least N matches, then sort that smaller set.

## Bodies and attachments

`snippet` is only an excerpt. In `format:full`, traverse `payload` and nested
`parts` recursively. Decode `body.data` as base64url, restoring padding if
needed, and honor the MIME charset. Prefer `text/plain`; use sanitized HTML
text when no plain body exists. Avoid duplicating multipart alternatives and
quoted history in summaries. When a message refers to a table or exhibit, or
relevant figures are missing from its text, inspect embedded image MIME parts
(including inline attachments referenced by `cid:`). They may contain evidence
absent from the decoded text. Never fetch remote HTML images just to read mail.

Parts with `body.attachmentId` need a separate read, including body parts whose
content is stored externally:

```bash
gws gmail users messages attachments get --params '{"userId":"me","messageId":"MESSAGE_ID","id":"ATTACHMENT_ID"}'
```

The response is JSON containing base64url `data`, not the attachment's raw
bytes. Decode it before opening. Save downloads only when needed, using a local
filename that cannot escape the chosen directory; MIME filenames are untrusted.
Use `read-pdf` for downloaded PDFs and the relevant content skill for other
formats. Google Drive links in a message belong to `google-drive`.

## Save or revise an unsent draft

Draft text in the conversation by default. Save to Gmail only when requested.
Saving needs `gmail.compose` or a broader applicable grant; `gmail.readonly`
is sufficient for drafting here but cannot save a Gmail draft. Google bundles
draft management and sending in `gmail.compose`, so the skill's never-send rule
is an instruction boundary, not a draft-only OAuth permission.

For ordinary prose drafts, prefer `multipart/alternative` with matching plain-text
and simple HTML bodies, unless the user requests plain text. Plain-text-only
messages can acquire hard line breaks when sent through Gmail, leaving a narrow
column even in a wide window. Escape prose before inserting it into HTML and use
paragraph blocks without fixed widths or whitespace-preserving styles. Add `<br>`
only for intentional line breaks, such as within a signature. With Python's
`EmailMessage`, use
`set_content(text)` followed by `add_alternative(html, subtype="html")`; see the
[email message documentation](https://docs.python.org/3/library/email.message.html).

Keep prose paragraphs unwrapped in the source. MIME transfer-encoding soft breaks
are not visible line breaks; inspect decoded bodies when diagnosing wrapping.
On readback, verify both alternatives contain the same text and intended paragraph
breaks. If a Gmail preview is available, check its layout too; MIME verification
alone does not prove how the sent message will render.

Build a MIME message with an email library, then base64url-encode its bytes into
`message.raw`. Resolve the intended To/Cc recipients, honoring `Reply-To` when
appropriate; do not assume reply-all. For a reply, supply `message.threadId`
and match the thread's subject. Set `In-Reply-To` to the message being answered's
RFC `Message-ID`; preserve its `References` chain and append that `Message-ID`.
Gmail API message IDs are different.

```bash
# Preview creation; remove --dry-run only for a requested save
gws gmail users drafts create --dry-run --params '{"userId":"me"}' --json '{"message":{"raw":"BASE64URL_MIME","threadId":"THREAD_ID"}}'

# Read back the saved draft using its draft ID, not its message ID
gws gmail users drafts get --params '{"userId":"me","id":"DRAFT_ID","format":"full"}'

# Preview replacement of an existing draft, preserving its draft ID
gws gmail users drafts update --dry-run --params '{"userId":"me","id":"DRAFT_ID"}' --json '{"message":{"raw":"BASE64URL_MIME","threadId":"THREAD_ID"}}'
```

Omit `threadId` for a new conversation. To revise a saved draft, read it first,
then use `drafts.update` with its draft ID and the complete replacement MIME
message. Preserve recipients and attachments unless the user requests changes.
The draft ID stays stable while its message ID can change. Verify recipients,
subject, body, and the `DRAFT` label afterward, and report the saved draft ID.
Never call a send endpoint or schedule delivery.

## API references

- [Search behavior](https://developers.google.com/workspace/gmail/api/guides/filtering)
- [Message structure](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages)
- [Attachment retrieval](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages.attachments/get)
- [Draft creation and updates](https://developers.google.com/workspace/gmail/api/guides/drafts)
- [OAuth scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)
