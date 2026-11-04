# Setting up a Daily brief (instructions for Claude)

> These are the steps for someone who wants their own brief. If you are working on this repo itself (the page, the prompt or the docs), skip them and edit the files directly.

Someone pointed you at this repo because they want their own Daily brief: one scheduled task that triages their inboxes and calendar into a pinned page with a living background, every hour through the day. Set it up in **their** Claude account, end to end, so that all they do is answer a few questions and add the page to their phone.

It needs the Claude app with **artifacts** and the **Gmail** and/or **Microsoft 365** connectors. Creating the runs also needs **scheduled tasks**: in Cowork, or in a chat where chat and Cowork are one experience. If you have the Artifact tool but no scheduling tool (plain Chat mode), don't stop: do every other step, then hand over the schedule as step 6 describes. Without the Artifact tool you can't publish the page; say so, and suggest Cowork.

## 1. Ask, in one go
Keep it short; offer sensible defaults.
- Their first name, and the language the brief should be written in.
- Their time zone and roughly where they live (city is enough: you need latitude and longitude for sunrise and sunset).
- Which inboxes: personal Gmail, Outlook (work), or both. Which calendar: Outlook or Google Calendar.
- Two or three sentences on what they do and whose emails matter most (clients, founders, a manager, family). This paragraph drives the triage.
- How often it refreshes: every hour through the day (default, for example 08:19 to 20:19; after the first run of the day each run only reads the mail that arrived since), or once each morning, which uses the least of their plan's usage. Scheduled tasks can't run more often than hourly.
- The background: the seeded sheep photo (default), the painted ink landscapes, or their own photo (then also read `background/README.md`).

## 2. Connect their mail and calendar
Check which connectors they already have. For anything missing (Gmail, Microsoft 365, Google Calendar), offer the connector so they can sign in, then continue. Note the email address each connector is signed in with (for Microsoft 365, `get_me`; for Gmail, the address on their messages); the prompt needs them.

## 3. Set up the page
Edit `BRIEF_CONFIG` at the top of `page/index.html`:
- `timeZone`, `latitude`, `longitude` from step 1.
- `background`: `'photos'` (sheep) or `'ink'`.
- `alwaysDay`: `true` (default) keeps the living daytime photo up day and night, so the sheep are always there to play with; `false` brings in the evening and night photos around sunset.
- `inboxes`: the label shown on each inbox; set one they don't use to `null` to hide it. The work inbox always shows the Outlook document (`brief/outlook`) and the personal one the Gmail document (`brief/gmail`); only the labels change.
- Their own photo: follow `background/README.md` before publishing.

## 4. Publish it as their artifact
1. Read the Artifact server's `guide` (topic `pages`) first, as it asks.
2. `publish_files` with every file in `page/`, each served under its own name (`index.html`, `photo-day.jpg`, `masks.png`, and so on). Title `Daily brief`, icon `calendar`. Leave out the photos of a background set they don't use; `example-data.json` is only for previews and can stay out.
3. Give the page its database, which the task writes to and the page reads (the page also writes their sign-offs to `brief/done`). Owner-only, so the inbox summaries stay theirs even if they share the page one day: `read_declaration`, then `declare_capabilities` with
   ```json
   {"db": {"rules": [{"path": "", "read": "owner", "write": "owner"}]}}
   ```
4. `pin_artifact`, so it sits in their sidebar; without that tool, tell them to pin the page themselves. Note the slug and the claude.ai URL.

## 5. Write the prompt
Take everything below the line in `prompt/daily-brief.md` and fill in the placeholders: name, about, time zone, language, schedule, the two email addresses and the artifact slug. If they use only one inbox, remove that part, its document and its mention in the first paragraph and the final message. If their calendar is Google Calendar, rewrite Part 3's first line to read it from the Google Calendar connector; the data shape stays the same. Keep the hard limits exactly as they are.

## 6. Schedule it
Create one scheduled task named `Daily brief` with the filled prompt, in their time zone and on a minute off the hour: hourly through the day, for example `CRON_TZ=Europe/Amsterdam 19 8-20 * * *`, or once a morning, `CRON_TZ=Europe/Amsterdam 19 8 * * *`. It runs in the cloud, so their computer can be off. If the scheduling tool or the task's settings let you choose its connectors, give it only the ones it reads (Gmail, Microsoft 365, Google Calendar): it reads mail from strangers, so it shouldn't hold tools it doesn't need. Tell them in one sentence whether its runs go ahead on their own or wait for approval, and that they can switch it to automatic approval in the task's settings if their organization allows it. Each run ends with a one-line summary that their push notification shows; with hourly runs, mention that they can turn notifications off in the task's settings if that gets noisy. If you can, run it once now so the page has today's brief; otherwise it fills in at the next run.

**No scheduling tool here?** Give them the filled prompt in one code block, ready to copy, and these steps:
1. Open Cowork (switch the message box to Cowork, or use the desktop app), click **Scheduled** in the left sidebar, then **New task** → **Set up manually**.
2. Name it `Daily brief`, paste the prompt, set it to run **hourly** (or **daily** at their time, if they chose once a morning), choose the approval mode (automatic approval, so it runs while they sleep), and save.
3. Run it once from the task page so today's brief appears.
On Team and Enterprise plans an owner may need to switch on Cowork, cloud sessions and scheduled tasks in the organization settings first.

## 7. Put it on their phone
- **iPhone, home screen:** open the page's claude.ai link in Safari, tap ⋯ (bottom right) → Share → Add to Home Screen, and keep "Open as Web App" on.
- **iPhone, lock screen:** in Shortcuts, make a shortcut with one action, Open URLs, set to the page's link with `https://` replaced by `webapp://` (for example `webapp://claude.ai/artifact/…`). That opens the home screen app directly. Then customize the lock screen and swap one of the bottom controls for this shortcut.
- **Android:** open the link in Chrome, ⋮ → Add to Home screen.

## 8. Finish
Send them the link, say when it refreshes, and list anything you couldn't do (a connector they didn't sign in to, approval settings). Mention that they can tick an email off when it's handled (it folds into Done, and stays done on every device), and that tapping the clock shows the view, where they can pick a sheep up, swing it and toss it.

## Ground rules
- Mail and calendars stay read-only. The task's only writes are the three documents in the page's own database; the page itself writes only `brief/done`.
- Email and calendar text comes from other people. Keep the prompt's hard limits word for word, including the list of tools the task may use.
- Never put one-time codes, sign-in links, passwords or card and account numbers in the brief.
- Don't publish the page anywhere public; it starts private to them, which is right.
