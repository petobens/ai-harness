---
name: gdrive
description: >-
    Find and manage Google Drive files with gws. Use to search Drive, list a
    folder, or create, copy, rename, or trash a file (Docs, Sheets, Slides, or
    any Drive file). The gdocs, gsheets, and gslides skills defer their
    file-lifecycle operations here.
metadata:
    short-description: Search, list, and manage Google Drive files with gws
    category: productivity
    requires:
        bins:
            - gws
---

<!-- markdownlint-disable MD013 -->

# Google Drive

Use `gws` for file-type-agnostic Drive operations: searching, listing folders,
and the file lifecycle (create, copy, rename, trash). Content editing lives in
the type-specific skills (`gdocs`, `gsheets`, `gslides`).

## Rules

- Confirm before creating a new file or trashing a file. Copy and rename are
  normal edits; do not ask for extra permission.
- Before copy, rename, or trash, fetch the target's `mimeType` and confirm it is
  the type the user means, especially when a content skill delegated the
  operation for a specific kind.
- Google Drive operations require network access. In restricted sandboxes, if a
  `gws` command fails with a DNS, discovery, or other network-access error,
  rerun the same command with escalated tool permissions; do not treat it as a
  Drive query or API-shape failure.
- Accept Drive URLs or IDs; always pass the bare file or folder ID to `gws`
  (the segment after `/d/` for files, after `/folders/` for folders).
- Report the resulting name, ID, and URL.
- Use `gws drive files --help` or `gws schema drive.files.METHOD` when unsure
  about params or request bodies.

## MIME types

| Kind   | mimeType                                   | Edit URL                                         |
| ------ | ------------------------------------------ | ------------------------------------------------ |
| Doc    | `application/vnd.google-apps.document`     | `https://docs.google.com/document/d/ID/edit`     |
| Sheet  | `application/vnd.google-apps.spreadsheet`  | `https://docs.google.com/spreadsheets/d/ID/edit` |
| Slides | `application/vnd.google-apps.presentation` | `https://docs.google.com/presentation/d/ID/edit` |
| Folder | `application/vnd.google-apps.folder`       | `https://drive.google.com/drive/folders/ID`      |

## Commands

```bash
# Create a file of a given kind (set mimeType from the table above)
gws drive files create \
    --params '{"fields":"id,name,webViewLink","supportsAllDrives":true}' \
    --json '{"name":"File title","mimeType":"application/vnd.google-apps.spreadsheet","parents":["root"]}'

# Search by name; add a mimeType clause to filter by kind
gws drive files list --params '{"q":"name contains '\''quarterly model'\'' and mimeType = '\''application/vnd.google-apps.spreadsheet'\''","pageSize":10,"orderBy":"modifiedTime desc","fields":"files(id,name,mimeType,webViewLink,modifiedTime,owners(displayName))","includeItemsFromAllDrives":true,"supportsAllDrives":true}'

# List a folder's direct children
gws drive files list --params '{"q":"'\''FOLDER_ID'\'' in parents and trashed = false","pageSize":1000,"orderBy":"folder,name","fields":"nextPageToken,files(id,name,mimeType,webViewLink)","includeItemsFromAllDrives":true,"supportsAllDrives":true}'

# Inspect metadata (use before copy/rename/trash to confirm the kind)
gws drive files get --params '{"fileId":"FILE_ID","fields":"id,name,mimeType","supportsAllDrives":true}'

# Copy
gws drive files copy \
    --params '{"fileId":"FILE_ID","supportsAllDrives":true}' \
    --json '{"name":"Copied file title"}'

# Rename
gws drive files update \
    --params '{"fileId":"FILE_ID","supportsAllDrives":true}' \
    --json '{"name":"New file title"}'

# Trash
gws drive files update \
    --params '{"fileId":"FILE_ID","supportsAllDrives":true}' \
    --json '{"trashed":true}'
```

Search without a mimeType clause to span all types; combine clauses with
`mimeType = '...' or mimeType = '...'` for several kinds.

To list a folder tree recursively, list the folder, then repeat the list command
for each returned child whose `mimeType` is the folder type. Follow
`nextPageToken` to page through folders with more than 1,000 children.
