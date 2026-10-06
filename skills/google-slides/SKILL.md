---
name: google-slides
description: >-
    Reads, inspects, edits, and builds Google Slides with gws. Use when the user
    asks to read or inspect a deck, replace or restyle slide text, add,
    duplicate, or delete slides, copy a template slide, or render slides to
    check their visual fit. Supports any deck, with Muttdata defaults for new
    presentations. Visual execution, not content strategy.
metadata:
    short-description: Read, edit, and build Google Slides with gws
    category: productivity
    requires:
        bins:
            - gws
            - curl
            - jq
            - pass
---

# Google Slides

Use `gws` to read, inspect, edit, build, and render Google Slides. For existing
decks, preserve their design unless the user requests a restyle. For new decks,
use the user's chosen template or design; default to the Muttdata conventions
below when none is specified. Adding slides to an existing deck should follow
that deck's design, including when it is not a Muttdata deck.

The work is visual execution, not content strategy. Content — storyline, titles,
chips, bullets, template recommendations — may already be decided upstream. Do
not invent the argument; render the provided content by changing only the text
needed. When the content names a recommended template slide, treat that as a
visual hint, not a content instruction.

## Role boundaries

- These boundaries govern how you create and edit slides; plain reads and
  inspections have no such limits. When editing, you own visual execution, not
  content strategy — assume titles, chips, and bullets may already be final.
- Do not rewrite content unless necessary for visual fit. Prefer layout
  adaptation over wording changes.
- If content is too dense, preserve readability and suggest splitting the slide
  rather than shrinking typography aggressively.
- If substantial net-new content would be needed to complete a slide, say a
  content pass is needed rather than expanding the argument yourself. At most
  make minimal wording fixes for fit, grammar, truncation, or parallelism.

## Muttdata decks

These defaults apply when creating a Muttdata deck, maintaining its template
library, or creating a new deck without another specified design. They do not
restyle unrelated decks.

Muttdata template deck:
`1_dE4_JqjIfj-aL30WJvxpV0YCgoPbJsQHOr8z1gJHCo`
(`https://docs.google.com/presentation/d/1_dE4_JqjIfj-aL30WJvxpV0YCgoPbJsQHOr8z1gJHCo/edit`).

- Build new Muttdata slides from the best matching template slide and preserve
  its design. Template-library expansion may use user-specified reference decks.
- In the Muttdata template, content-slide titles use DM Sans bold, 24 pt on a
  720 × 405 pt slide; scale proportionally for other page sizes. Keep this size
  consistent instead of shrinking individual titles to fit. Use two lines or
  adjust the layout when needed. Covers, section dividers, and hero statements
  retain their separate display hierarchy.
- Preserve the original rounded title-marker image from the template layout.
  When a copied layout needs a replacement, reuse that asset and its placement
  rather than rebuilding it with rectangular shapes.

## Rules

- Creating a presentation, copying a slide into a deck, or trashing a
  presentation requires user authorization. Use authorization already given in
  the request or conversation; ask only when the action is outside that scope.
  Normal text edits to an existing deck need no extra confirmation.
- Do not ask for task-level permission before safe local prep, such as
  inspecting a deck, building request JSON in `/tmp`, or running `--dry-run`. If
  the environment requires sandbox approval, request it as a tool permission
  only.
- Google Slides reads and writes require network access. In restricted
  sandboxes, if a `gws` command fails with a DNS, discovery, or other
  network-access error, rerun the same command with escalated tool permissions;
  do not treat it as a presentation or API-shape failure.
- When reading a deck, keep the content in agent context and return only a brief
  confirmation with the title, ID, URL, and inspected slides by default. Do not
  paste slide text, a full extraction, or a summary unless the user explicitly
  asks for one.
- Always inspect the target presentation before editing, and review every edited
  or created slide for visual fit before reporting done.
- Make the smallest safe change that achieves the goal, and preserve consistency
  across the whole deck.
- The first delivered version of each slide must already be visually clean — no
  known overflow, clipping, excessive line breaks, or poor fit left for a later
  round.
- Accept Slides URLs or IDs; always pass the bare presentation ID (the segment
  after `/presentation/d/`) to `gws`.
- Use `gws schema slides.presentations.METHOD` or `gws slides --help` when unsure
  about params or request bodies.
- Report final title, ID, URL, and operations performed.

## Files (create, find, copy, rename, trash)

Use the `google-drive` skill for these. A presentation's mimeType is
`application/vnd.google-apps.presentation`; pass it when creating, and confirm
the target matches it before copy, rename, or trash. (Note: "copy" here means
copying a whole presentation file in Drive, a different operation from copying
a single template slide between decks (see _Copying a template slide across
decks_).)

```bash
# Create a blank presentation
gws drive files create \
    --params '{"fields":"id,name,webViewLink","supportsAllDrives":true}' \
    --json '{"name":"Presentation title","mimeType":"application/vnd.google-apps.presentation","parents":["root"]}'
```

## Reading and inspecting

Reading and inspecting are different intents. Read when you need the deck's
content — to show it or answer a question about it. Inspect when you are preparing
an edit and need element `objectId`s, placeholder types, text run indices,
geometry, and styling. Both save the response to `/tmp` first, then parse the
local JSON, which avoids losing the read to terminal output truncation or a
transient network error, and verify it is a presentation payload, not an API
error object:

```bash
jq -e '(has("error") | not) and (.slides | type == "array")' /tmp/slides-read.json
```

If it contains an `error` with DNS, discovery, connection, or temporary lookup
wording, rerun the same `gws` command with escalated network permissions. Do not
pipe a failed response into `jq` as if it were a deck.

### Reading content

For a read, fetch the full payload — omit the `fields` mask so nothing is left
out, including text inside grouped elements and table cells:

```bash
gws slides presentations get \
    --params '{"presentationId":"PRES_ID"}' \
    2> /dev/null > /tmp/slides-read.json
```

Use the compact slide index for a read confirmation; extract full slide text only
when the user explicitly asks. The extractor recurses through grouped children and
table cells:

```bash
jq -r '
  def texts:
    [
      .shape?.text?.textElements[]?.textRun?.content,
      (.elementGroup?.children[]? | texts),
      .table?.tableRows[]?.tableCells[]?.text?.textElements[]?.textRun?.content
    ] | flatten | map(select(. != null));

  "TITLE\t" + (.title // ""),
  (.slides | to_entries[] |
    ["SLIDE", (.key + 1 | tostring), .value.objectId,
      ([.value.pageElements[]? | texts[]]
       | map(gsub("\u000b"; " ")
       | gsub("\n"; " ")
       | gsub("  +"; " ")
       | gsub("^ +| +$"; ""))
       | map(select(length > 0))
       | .[0:4]
       | join(" | "))
    ] | @tsv)
' /tmp/slides-read.json
```

Text baked into images, charts, or other raster assets is not API-native; render
a thumbnail (see _Verifying_) and inspect visually when that content matters.

### Inspecting for edits

For edit prep, add a field mask to surface the `objectId`s, placeholder types, run
indices, geometry, and styling you need while keeping the response manageable; it
also reaches text inside grouped elements and table cells:

```bash
fields="title,pageSize,slides(objectId,\
slideProperties.layoutObjectId,pageElements(objectId,size,transform,\
shape(shapeType,placeholder,text(textElements(startIndex,endIndex,\
textRun(content,style),paragraphMarker(bullet,style)))),\
elementGroup(children(objectId,size,transform,\
shape(shapeType,placeholder,text(textElements(startIndex,endIndex,\
textRun(content,style),paragraphMarker(bullet,style)))),image,\
table(tableRows(tableCells(text(textElements(startIndex,endIndex,\
textRun(content,style),paragraphMarker(bullet,style)))))))),image,\
table(tableRows(tableCells(text(textElements(startIndex,endIndex,\
textRun(content,style),paragraphMarker(bullet,style)))))))))"
params="$(jq -nc \
    --arg fields "$fields" \
    '{presentationId:"PRES_ID",fields:$fields}')"
gws slides presentations get \
    --params "$params" \
    2> /dev/null > /tmp/slides-read.json
```

From the output, note for each shape you intend to edit: its `objectId`, the
`placeholder.type` (e.g. `TITLE`, `SUBTITLE`, `BODY`), the text run
`startIndex`/`endIndex` (zero-based, end exclusive — these are the ranges you
target for styling), and its position/size. Element order is z-order.

For layout checks, use the element's transformed bounds, not raw `size`: Slides
may normalize dimensions and store the visible scale in `transform`. Compose
parent transforms for grouped elements and account for the declared units.

When post-processing this output programmatically, account for two quirks:
`startIndex` is omitted entirely when it is `0` (read it as `.get("startIndex",
0)`, never index directly), and `gws` prints a `Using keyring backend` banner to
stderr. Pipe with `2>/dev/null` when feeding stdout to a JSON parser; never
`2>&1`, which merges that banner into the JSON and breaks the parse.

## Editing an existing deck

Text and styling changes on slides already in the deck. Creating new slides is
template-first and covered below.

### Text and style edits

Every edit below is one `gws slides presentations batchUpdate` call (requests
apply atomically; one invalid request rolls back the whole batch). Preview
requests with `--dry-run`; it does not replace API read-back or visual
verification. For non-trivial JSON, write
`/tmp/slides.json` and pass `--json "$(cat /tmp/slides.json)"`.

```bash
gws slides presentations batchUpdate --dry-run \
    --params '{"presentationId":"PRES_ID"}' \
    --json "$(cat /tmp/slides.json)"
```

**Replace text (the common case).** `replaceAllText` is the simplest way to
swap template placeholder text. Scope it to one slide with `pageObjectIds`.

```json
{
    "requests": [
        {
            "replaceAllText": {
                "containsText": {
                    "text": "{{TITLE}}",
                    "matchCase": true
                },
                "replaceText": "Q3 Revenue",
                "pageObjectIds": [
                    "SLIDE_OBJECT_ID"
                ]
            }
        }
    ]
}
```

**Replace a uniformly styled shape's text.** Read its text-run and paragraph
styles, then delete all text, insert the replacement, and reapply those styles.
For mixed formatting, preserve each run's emphasis and paragraph/bullet structure;
applying the first run's style to the whole shape flattens the original design.
Map emphasis to complete words in the replacement, not proportional character
offsets that can split words across styles. The example below uses uniform text:

```json
{
    "requests": [
        {
            "deleteText": {
                "objectId": "SHAPE_ID",
                "textRange": {
                    "type": "ALL"
                }
            }
        },
        {
            "insertText": {
                "objectId": "SHAPE_ID",
                "insertionIndex": 0,
                "text": "New copy"
            }
        },
        {
            "updateTextStyle": {
                "objectId": "SHAPE_ID",
                "textRange": {
                    "type": "ALL"
                },
                "style": {
                    "bold": true,
                    "fontSize": {
                        "magnitude": 18,
                        "unit": "PT"
                    }
                },
                "fields": "bold,fontSize"
            }
        }
    ]
}
```

**Restyle existing text** over an explicit range (indices from inspect; omit the
range or use `{"type":"ALL"}` for the whole shape):

```json
{
    "requests": [
        {
            "updateTextStyle": {
                "objectId": "SHAPE_ID",
                "textRange": {
                    "type": "FIXED_RANGE",
                    "startIndex": 0,
                    "endIndex": 12
                },
                "style": {
                    "bold": true,
                    "foregroundColor": {
                        "opaqueColor": {
                            "rgbColor": {
                                "red": 0.0,
                                "green": 0.06,
                                "blue": 1.0
                            }
                        }
                    }
                },
                "fields": "bold,foregroundColor"
            }
        }
    ]
}
```

Supported style fields mirror the Slides API: `bold`, `italic`, `underline`,
`strikethrough`, `smallCaps`, `foregroundColor` (RGB floats `0..1`), `fontFamily`,
`fontSize` (`{magnitude, unit:"PT"}`), and `link` (`{url}`). Always set `fields`
to exactly the keys you changed.

**Slide-level operations** (each a single request in a `batchUpdate`):

- Create a blank slide: `createSlide` with optional `insertionIndex` (zero-based)
  and `slideLayoutReference.predefinedLayout`. Prefer copying a template slide
  over `createSlide`.
- Duplicate a slide: `duplicateObject` with `{objectId:"SLIDE_ID"}`; reposition
  the copy with a follow-up `updateSlidesPosition`
  (`{slideObjectIds:["NEW_ID"],insertionIndex:N}`).
- Delete a slide: `deleteObject` with `{objectId:"SLIDE_ID"}`.

For anything the above do not cover — shapes, images, tables, geometry,
recoloring — build the requests directly against the Slides `batchUpdate` API.

### Rendering a slide outline

When the input includes an internal plan, slide-number labels, or HTML comments,
use them to guide construction without rendering them as slide copy. Preserve
content hierarchy when mapping claims and supporting text into lists or cards.
A Markdown table can supply a comparison, timeline, or chart; follow any visual
specification and preserve its relationships and source notes. Render chart
input data as the chart, without duplicating the input table unless requested.

### Text replacement and fitting

- For newly generated decks, use titles and optional chips instead of subtitles,
  unless the user requests subtitles. Remove unused subtitle placeholders from
  copied layouts and rebalance the body when their removal leaves an awkward gap.
  Compare the visible gap below the title with the space above the footer; move
  the complete content group, including cards, labels, text, icons, and arrows.
  Check layout-inherited elements too. Before changing a shared layout or
  master, identify every slide it affects; include those slides in visual
  verification afterward.
- Change text content but preserve formatting. Take particular care not to flip
  bold to regular or regular to bold, and preserve font family, size, color,
  emphasis, alignment, and text-box structure unless the user requests a restyle
  or a small change is required for fit.
- A `**Chip:**` field is a short pill-style context label (e.g. "Overall
  Outlook"), not a subtitle or second title. Render it in an existing
  chip/badge/pill/tag element; if the copied template has none, choose a template
  slide that does rather than adding a subtitle box. Keep chip text short (one to
  three words) and preserve its fill, corner radius, typography, alignment, and
  position.
- Treat each text box or shape as a hard bounding box: text must fit fully inside
  without overflow, clipping, or collision. Use the template's original text as
  the practical maximum density.
- Let the container wrap text naturally. Do not add manual line breaks, paragraph
  breaks, or blank lines to force wrapping unless they are already in the
  template. Preserve the original paragraph structure when possible.
- If replacement text overflows, first remove unnecessary manual breaks or excess
  paragraph spacing. If it still does not fit, prefer a better template slide or
  split the content rather than forcing denser copy or shrinking type.
- For content-only edits, adjust geometry to fix overflow, overlap, clipping, or
  unbalanced space. Broader design changes should follow the user's request.
- Before finishing, review every edited text box for overflow, clipped text,
  empty lines, unnatural wrapping, and over-dense copy.

### Maintaining the template library

When the user explicitly asks to expand or clean the template deck, source slides
may come from their specified reference decks. Copy them natively, compare with
existing layouts to avoid near-duplicates, and place additions in the matching
section. Use structural titles so future agents can select layouts by purpose.

When lorem ipsum is requested, replace complete text fields or paragraphs, not
substrings inside words. Keep numbering and use consistent dummy values for
metrics. Inspect grouped text, table cells, speaker notes, links, and labels baked
into images for source content. Clear or neutralize source-specific content within
the authorized cleanup scope, preserving brand assets and reusable icons.

## Creating slides (template-first)

- Choose the source design using the scope rules above. Prefer a suitable slide
  in the target deck or selected template; copy the best structural match (see
  _Copying a template slide across decks_) and adapt its content.
- Preserve native elements when copying a layout. Build a new layout when the
  requested design has no suitable source or copying is unavailable.
- Treat the copied slide as the source of truth for layout, spacing, typography,
  shapes, containers, alignment, emphasis, and footer behavior.
- In layout libraries, use structural slide titles as selection signals rather
  than content to reproduce.
- If an existing target slide is a poor fit, prefer replacing it with a copied
  template slide rather than redesigning it by hand.
- Preserve the source styling unless the user requests a design change or an
  adjustment is needed to prevent a layout defect.

### Template slide selection

Before adding a slide, review the selected source deck and pick the slide whose
structure best matches the content. Match by layout, not superficial text
similarity. Common structures: title, section divider, slide with a top-right
chip/badge, single statement, 2-column comparison, 3-column framework, card grid,
timeline, quote/highlight, image + text, metrics/KPI, process/flow.

Prefer the template slide whose number of text fields, grouping, hierarchy, chip
placement, and density most closely match the target content.

Selection priority:

1. Exact match on a recommended template slide title, when available and
   structurally sound.
2. Best structural fit for the content.
3. Preservation of visual quality and readability.
4. Recommended slide number, when provided.
5. Variety across the deck.
6. Minimal editing effort.

Variety guardrail: maximize template variety across the deck while preserving
coherence, but never choose a worse-fitting slide just for variety. When several
are equally suitable, prefer one not yet used (or used less) in the deck. Reuse
the exact same template slide only when it is clearly the best fit or when
consistency across a repeated sequence is desirable. When in doubt, choose the
more restrained option and stay as close to the original template as possible.

### Copying a template slide across decks

The Slides API cannot copy a slide between presentations while preserving its
design, so this goes through the Muttdata Apps Script web app. Its deployed
source is [copy-slides-webapp.gs](scripts/copy-slides-webapp.gs); edit that
copy and redeploy when the web app changes. Prefer a source slide `objectId`
(from inspecting the template deck); `sourceSlideIndex` (1-based) is the
fallback. `insertionIndex` sets the destination position; omit to append.

```bash
url="$(pass show gcloud/appscript/copy-slides/webapp-url)"
secret="$(pass show gcloud/appscript/copy-slides/webapp-secret)"
jq -nc \
    --arg secret "$secret" \
    --arg src SOURCE_PRES_ID \
    --arg dst DEST_PRES_ID \
    --arg slide SOURCE_SLIDE_OBJECT_ID \
    '{secret:$secret, sourcePresentationId:$src, destinationPresentationId:$dst, sourceSlideObjectId:$slide}' |
    curl -sSL -H 'Content-Type: application/json' -d @- "$url"
```

A success response is `{"ok":true,"newSlideObjectId":"..."}`; failure is
`{"ok":false,"error":"..."}` or an HTTP status ≥ 400. After copying, inspect the
new slide and replace only the text content needed.

## Verifying

The deck JSON cannot reveal whether text overflows its box, collides, or wraps
badly — only a render can. For each slide you created or edited, render it and
look at the result before reporting done:

```bash
# Returns a PNG URL for one rendered slide
url="$(gws slides presentations pages getThumbnail \
    --params '{
        "presentationId": "PRES_ID",
        "pageObjectId": "SLIDE_OBJECT_ID",
        "thumbnailProperties.thumbnailSize": "LARGE"
    }' \
    2> /dev/null | python3 -c \
    'import json,sys; print(json.load(sys.stdin)["contentUrl"])')"
curl -sSL "$url" -o /tmp/slide.png
```

Then open `/tmp/slide.png` with an image-viewing tool and inspect it for overflow,
clipping, collisions, awkward wrapping, contrast, and vertical balance between
the title, body, and footer. Fix any defect and re-render before finishing.

`getThumbnail` is an expensive read request for quota, so use it as a final
visual check per created or edited slide, not after every intermediate edit.
Structured read-back (text runs, indices, styles) stays the right tool for
verifying content and styling; the render is specifically for visual fit.

## What to avoid

- Rebuilding a suitable native source slide without a reason.
- Inferring a design from screenshots when native source elements are available.
- Imposing Muttdata styling on a deck with another specified design.
- Reformatting copied slides unnecessarily, or carelessly changing bolding,
  emphasis, shape geometry, or layout rhythm.
- Overlapping text, icons, or shapes; text overflow, clipping, truncated
  paragraphs, hidden lines, or body copy spilling outside its container.
- Adding unnecessary line breaks, blank lines, or manual wraps that make text
  taller than needed.
- Exceeding the text capacity suggested by the template's original content.
- Broken geometry or misalignment introduced during text replacement.
- Leaving any slide with unresolved overlap, overflow, clipping, or accidental
  formatting drift.
