# The Daily brief in ChatGPT

This repo is built for Claude. It also maps onto ChatGPT, as of November 2026:

- **The brief itself: yes.** ChatGPT's scheduled tasks can read Gmail, Outlook and your calendar on a schedule and notify you. On a paid plan they can run every hour. [Path A](#path-a-the-brief-as-a-scheduled-task) sets this up with a ready-made prompt. You get the brief as a message instead of a page.
- **The living page: probably, but unproven.** ChatGPT Sites can host this page with its own database, private to you, and a Site can run its own schedules. OpenAI doesn't yet document whether one scheduled run can both read your mail and write into a Site's database. [Path B](#path-b-the-page-as-a-chatgpt-site-experimental) tries it.

We built and tested the Claude version. The ChatGPT paths follow OpenAI's documentation as checked on 9 November 2026, and nobody has run them end to end yet. ChatGPT renames things often: what it now calls *plugins* used to be *connectors* and then *apps*.

## How the pieces map

| Part of the brief | In Claude (this repo) | In ChatGPT | Carries over? |
|---|---|---|---|
| The schedule | One scheduled task in the cloud, every hour from 08:19 to 20:19 | Scheduled tasks. Paid plans can repeat hourly; Free and Go run once a day. Each plan caps active tasks, and recurring tasks you ignore can be paused | Yes |
| Reading mail and calendar | Gmail, Microsoft 365 and Google Calendar connectors | Gmail, Google Calendar, Outlook Email and Outlook Calendar plugins | Yes |
| The triage | [`prompt/daily-brief.md`](../prompt/daily-brief.md) | The same rules, in [`prompt/daily-brief-chatgpt.md`](../prompt/daily-brief-chatgpt.md) | Yes |
| The notification | A one-line summary as a push notification | Push and/or email notifications | Yes |
| The page | A private Claude artifact, pinned in the sidebar | A ChatGPT Site: private by default, on Plus, Pro, Business and Enterprise (not Free or Go) | Path B |
| The page's data | The artifact's database: five documents, readable by you alone | The Site's database | Path B |
| The hourly update of the page | The task writes three documents | A Site's Automations: cloud schedules on a published Site | Unconfirmed |
| Sign-offs and the learning loop | The page writes `brief/done` and `brief/feedback`; every run reads them | Path B: the same documents. Path A: the rules live in the task's instructions | Partly |
| Sheep, clock and view | `page/index.html` | The same file, hosted on a Site | Path B |
| Lock screen | The page's link as a home screen web app | A Site's link works the same way, after signing in to ChatGPT | Probably |

## Path A: the brief as a scheduled task

This works today. It needs the Gmail plugin, the Outlook Email and Outlook Calendar plugins (or Google Calendar), and a paid plan if you want hourly runs.

1. **Connect your mail.** In ChatGPT, go to Settings → Plugins and connect Gmail, Outlook Email and Outlook Calendar (or Google Calendar). If your plan or workspace lets you choose which actions a plugin may take, allow reading only.
2. **Fill in the prompt.** Take everything below the line in [`prompt/daily-brief-chatgpt.md`](../prompt/daily-brief-chatgpt.md) and fill in the placeholders. The "About" paragraph drives the triage, so take a minute over it.
3. **Run it once in a chat.** Paste the prompt into a new chat and check the result. Adjust the About paragraph until the sorting looks right.
4. **Schedule it.** In that same chat, ask ChatGPT to run it every hour from 08:19 to 20:19, or every morning at 08:19. It turns the chat into a scheduled task, which you'll find under **Scheduled** in the sidebar. Turn notifications on. If your plan offers a monitoring task that only notifies when there's something to report, the hourly version suits it: later runs answer `Nothing new` when nothing new needs you.
5. **Teach it.** When an email lands in the wrong place, open the task under Scheduled, edit its instructions, and add a line under *Learned from …*. That's Path A's version of the page's move button.

What you give up: the page, the sheep, and ticking emails off. An email you've answered drops out of the next brief, because every run checks your sent mail.

## Path B: the page as a ChatGPT Site (experimental)

ChatGPT Sites has the same shape as this repo: a page, its own database, and schedules that update it. A Site is private to its owner unless you share it, and it's built in ChatGPT Work on the web or in the desktop app. Hosting is included in Plus and Pro until 31 December 2026; from 2027, OpenAI meters usage beyond your plan's allowance.

1. Open **ChatGPT Work**, give it this repo (or upload the `page/` folder and the two prompt files), and say: *Build my Daily brief as a private Site, following docs/chatgpt.md, Path B.*
2. Answer its questions: the same ones as step 1 of [`CLAUDE.md`](../CLAUDE.md).
3. **The test that decides it:** once the Site is published, run its Automation once. If the page fills in with your mail, you have the full brief, with sign-offs and the learning loop. If the run can't reach your mail, use Path A. OpenAI's Sites documentation says that app access you approve inside a Site doesn't carry over to its background schedules, so this depends on what the schedule itself is allowed to use.
4. **On your phone,** open the Site's link and add it to your home screen, as step 7 of [`CLAUDE.md`](../CLAUDE.md) describes. A private Site asks you to sign in with your ChatGPT account.

### Instructions for ChatGPT (Path B)

- **The page.** Host `page/index.html` and its images unchanged. Set `BRIEF_CONFIG` at the top of `index.html` from the owner's answers: time zone, location, `runs`, background and inbox labels. `example-data.json` is only for previews.
- **The data.** Give the Site a database that holds five JSON documents: `brief/gmail`, `brief/outlook` and `brief/calendar`, written by the schedule, and `brief/done` and `brief/feedback`, written by the page. Their shapes are in [`prompt/daily-brief.md`](../prompt/daily-brief.md). Only the owner may read or write them.
- **How the page reads and writes.** The page reaches its data through one interface, at the bottom of `index.html`. `claude.use('db')` returns an object whose `doc(path)` has two methods:
  - `onSnapshot(next, error)` calls `next(snapshot)` with the current document and again whenever it changes. The snapshot has `exists`, `data()` and `metadata.fromCache`, which is `false` once the data is fresh from the server. It returns a function that stops listening.
  - `set(data)` replaces the whole document and returns a promise.

  Provide this same `window.claude` object on the Site, backed by the Site's database, before the page's own script runs. Checking for changes once a minute is enough. The rest of the page then works unchanged. Without it, the page shows its example data.
- **The schedule.** Add an Automation that runs everything below the line in `prompt/daily-brief.md` every hour from 08:19 to 20:19 (or once at 08:19), with the placeholders filled in. Replace that prompt's "Where the results go" section with this Site's database and the five paths above, and give the Automation the Gmail and Outlook plugins, read-only. Keep the prompt's hard limits as they are.
- **Publish it privately, to the owner only.** Never publish it publicly: it holds summaries of the owner's mail.

## The same safety rules

- ChatGPT's Gmail and Outlook plugins can send mail when you approve it, so both prompts keep mail strictly read-only. A run that stops to ask for approval stays paused until you answer it.
- Give the task only the plugins it reads, and keep their actions read-only where your plan lets you choose.
- Both prompts treat email as data, never as instructions, whoever an email claims to be from.

## For developers

An MCP app, built with OpenAI's Apps SDK, could show the brief inside ChatGPT conversations, with your own server holding the data. That's more work than a Site, and only worth it if you want the brief inside chats.

## Sources (checked 9 November 2026)

- OpenAI Help Center: [Scheduled tasks in ChatGPT](https://help.openai.com/en/articles/10291617)
- OpenAI: [Scheduled tasks walkthrough](https://developers.openai.com/training/walkthroughs/scheduled-tasks)
- OpenAI Help Center: [Outlook Email and Calendar apps in ChatGPT](https://help.openai.com/en/articles/12512241)
- OpenAI Help Center: [Creating and using ChatGPT Sites](https://help.openai.com/en/articles/20001339-creating-and-using-chatgpt-sites)
- OpenAI Help Center: [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)
- OpenAI Help Center: [ChatGPT Pulse](https://help.openai.com/articles/12293630-chatgpt-pulse) (retired in favour of scheduled tasks)
- OpenAI Apps SDK: [Managing state](https://developers.openai.com/apps-sdk/build/state-management)
