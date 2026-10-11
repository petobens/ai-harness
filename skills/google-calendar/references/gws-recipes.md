# Calendar gws recipes

## Access

Use the existing `gws` account and check `gws auth status` for local auth
configuration. Never print exported credentials or tokens. A small
`calendarList.list` request verifies live access.

If the API returns `accessNotConfigured`, enable Google Calendar API in the
OAuth client's Cloud project using the error's enable URL. Its service name is
`calendar-json.googleapis.com`. Missing OAuth scopes are a separate problem.
`https://www.googleapis.com/auth/calendar.readonly` supports calendar discovery,
event reads, and free/busy; a broader existing grant also works.

For a new read-only setup, use
`gws auth login --readonly --services calendar`. When reauthorizing an
existing Workspace setup, preserve its required Drive, Docs, Sheets, and Slides
scopes using the scope picker or `--scopes` with the complete desired set. Add
Calendar read access without replacing existing write access with a read-only
service subset. Consult `gws auth login --help` for installed-version options.

## Calendars and agendas

Replace the example dates with the actual requested interval.

```bash
# Discover calendars, their access levels, and time zones
gws calendar calendarList list --params '{"maxResults":100,"fields":"nextPageToken,items(id,summary,primary,selected,accessRole,timeZone)"}'

# One local day's agenda, including recurring occurrences
gws calendar events list --params '{"calendarId":"primary","timeMin":"2026-10-12T00:00:00-03:00","timeMax":"2026-10-13T00:00:00-03:00","timeZone":"America/Argentina/Buenos_Aires","singleEvents":true,"orderBy":"startTime","showDeleted":false,"maxResults":250,"fields":"nextPageToken,timeZone,items(id,iCalUID,summary,status,start,end,htmlLink,location,attendees(email,self,responseStatus),organizer,recurringEventId,originalStartTime,transparency,eventType)"}'

# Full details for meeting preparation
gws calendar events get --params '{"calendarId":"CALENDAR_ID","eventId":"EVENT_ID"}'
```

Pass `nextPageToken` as `pageToken` with the same parameters until exhausted.
Repeat the agenda query for each relevant calendar. For event searches, add `q`
and keep a suitable time window; it searches event text, not Gmail syntax.

`timeMin` filters event end times and `timeMax` filters start times, both
exclusively, so the query includes events overlapping the window. `orderBy`
`startTime` requires `singleEvents:true`. Recurring occurrences have their own
IDs; `recurringEventId` identifies the series and `originalStartTime` identifies
the original slot of a moved occurrence.

Timed events use `dateTime`; all-day events use `date`, with an exclusive end
date. Do not convert all-day dates through UTC. Ignore cancelled events for an
active agenda, and identify declined or tentative invitations when relevant.
When merging calendars, avoid counting the same invitation twice; inspect
`iCalUID` and occurrence timing if deduplication is needed.

## Availability

`freebusy.query` uses HTTP POST but is read-only. Query the relevant calendars
together, including the user's calendar when finding mutual availability.

```bash
gws calendar freebusy query --json '{"timeMin":"2026-10-12T09:00:00-03:00","timeMax":"2026-10-12T18:00:00-03:00","timeZone":"America/Argentina/Buenos_Aires","items":[{"id":"primary"},{"id":"PERSON@example.com"}]}'
```

Inspect each calendar's `errors` before interpreting its `busy` intervals.
Missing access or a lookup error does not mean free time. Busy intervals have
inclusive starts and exclusive ends. Merge overlaps and subtract them from the
requested working window, then keep gaps long enough for the meeting. An event
with `transparency:transparent` does not block time; do not treat every agenda
entry as busy when interpreting event details.

## API references

- [Event listing and time bounds](https://developers.google.com/workspace/calendar/api/v3/reference/events/list)
- [Event structure](https://developers.google.com/workspace/calendar/api/v3/reference/events)
- [Free/busy queries](https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query)
