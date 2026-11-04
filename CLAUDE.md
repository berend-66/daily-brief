# Setting up a Daily brief (instructions for Claude)

> These are the steps for someone who wants their own brief. If you are working on this repo itself (the page, the prompt or the docs), skip them and edit the files directly.

Someone pointed you at this repo because they want their own Daily brief: one scheduled task that triages their inboxes and calendar every morning into a pinned page with a living background. Set it up in **their** Claude account, end to end, so that all they do is answer a few questions and add the page to their phone.

It needs the Claude app (web, desktop or mobile) with **artifacts** and **scheduled tasks**, plus the **Gmail** and/or **Microsoft 365** connectors. Claude Code on its own can't publish the page; if you lack the Artifact or scheduling tools, say so and stop.

## 1. Ask, in one go
Keep it short; offer sensible defaults.
- Their first name, and the language the brief should be written in.
- Their time zone and roughly where they live (city is enough: you need latitude and longitude for sunrise and sunset).
- Which inboxes: personal Gmail, Outlook (work), or both. Which calendar: Outlook or Google Calendar.
- Two or three sentences on what they do and whose emails matter most (clients, founders, a manager, family). This paragraph drives the triage.
- What time it should refresh (default about 08:00, before they look at their phone).
- The background: the seeded sheep photo (default), the painted ink landscapes, or their own photo (then also read `background/README.md`).

## 2. Connect their mail and calendar
Check which connectors they already have. For anything missing (Gmail, Microsoft 365, Google Calendar), offer the connector so they can sign in, then continue. Note the email address each connector is signed in with (for Microsoft 365, `get_me`; for Gmail, the address on their messages); the prompt needs them.

## 3. Set up the page
Edit `BRIEF_CONFIG` at the top of `page/index.html`:
- `timeZone`, `latitude`, `longitude` from step 1.
- `background`: `'photos'` (sheep) or `'ink'`.
- `inboxes`: the label shown on each inbox; set one they don't use to `null` to hide it. The work inbox always shows the Outlook document (`brief/outlook`) and the personal one the Gmail document (`brief/gmail`); only the labels change.
- Their own photo: follow `background/README.md` before publishing.

## 4. Publish it as their artifact
1. Read the Artifact server's `guide` (topic `pages`) first, as it asks.
2. `publish_files` with every file in `page/`, each served under its own name (`index.html`, `photo-day.jpg`, `masks.png`, and so on). Title `Daily brief`, icon `calendar`. Leave out the photos of a background set they don't use; `example-data.json` is only for previews and can stay out.
3. Give the page its database, which the morning task writes to and the page reads: `read_declaration`, then `declare_capabilities` with
   ```json
   {"db": {"rules": [{"path": "", "read": "view", "write": "owner"}]}}
   ```
4. `pin_artifact`, so it sits in their sidebar. Note the slug and the claude.ai URL.

## 5. Write the morning prompt
Take everything below the line in `prompt/daily-brief.md` and fill in the placeholders: name, about, time zone, language, the two email addresses and the artifact slug. If they use only one inbox, remove that part, its document and its mention in the first paragraph and the final message. If their calendar is Google Calendar, rewrite Part 3's first line to read it from the Google Calendar connector; the data shape stays the same. Keep the hard limits exactly as they are.

## 6. Schedule it
Create one scheduled task named `Daily brief`, daily at the time from step 1 in their time zone (for example `CRON_TZ=Europe/Amsterdam 19 8 * * *`; pick a minute off the hour), with the filled prompt. It runs in the cloud, so their computer can be off. Tell them in one sentence whether its runs go ahead on their own or wait for approval, and that they can switch it to automatic approval in the task's settings if their organization allows it. If you can, run it once now so the page has today's brief; otherwise it fills in tomorrow morning.

## 7. Put it on their phone
- **iPhone, home screen:** open the page's claude.ai link in Safari, tap ⋯ (bottom right) → Share → Add to Home Screen, and keep "Open as Web App" on.
- **iPhone, lock screen:** in Shortcuts, make a shortcut with one action, Open URLs, set to the page's link with `https://` replaced by `webapp://` (for example `webapp://claude.ai/artifact/…`). That opens the home screen app directly. Then customize the lock screen and swap one of the bottom controls for this shortcut.
- **Android:** open the link in Chrome, ⋮ → Add to Home screen.

## 8. Finish
Send them the link, say when it refreshes, and list anything you couldn't do (a connector they didn't sign in to, approval settings). Mention that they can tap the clock to see the view, and that the background follows the time of day.

## Ground rules
- Mail and calendars stay read-only. The only writes are the three documents in the page's own database.
- Never put one-time codes, sign-in links, passwords or card and account numbers in the brief.
- Don't publish the page anywhere public; it starts private to them, which is right.
