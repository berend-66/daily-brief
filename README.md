# Daily brief

A morning brief for Claude that sits one tap from your lock screen.

Every morning, one scheduled task reads your inboxes and your calendar and writes them into one live page. It leads with what needs you, then what's worth a look and your calls for the week. The background follows the time of day, and the morning photo is alive: clouds drift and ten sheep graze inside the fence.

<p>
  <img src="docs/preview.jpg" width="360" alt="The Daily brief on a phone">
  <img src="docs/sheep.gif" width="288" alt="The living background: sheep grazing in the field">
</p>

## Set it up

Open Claude (web, desktop or mobile), give it this repo and say:

> Set up my daily brief from this repo.

Claude follows [`CLAUDE.md`](CLAUDE.md). It asks a few questions (your name, time zone, which inboxes, what you do), connects Gmail and/or Outlook, publishes the page to your account and schedules the morning run. At the end it walks you through putting the page on your phone's home screen and lock screen.

**You need:** Claude with artifacts and scheduled tasks, plus the Gmail and/or Microsoft 365 connectors (Google Calendar works too).

## What you get

- **One scheduled task**, every morning, in the cloud. Your computer can be off.
- **Your inboxes, triaged.** Gmail and Outlook, each sorted into *Needs you*, *Worth a look*, *Worth reading* (two newsletters at most) and counts of what was skipped.
- **Your calls** for today and the rest of the week: who's joining, and which ones clash.
- **One page** that updates itself. Tap *Need you* for everything waiting on you, with a button that opens each email. Fold an inbox you don't need right now. Tap the clock to see the view.
- **Read-only.** It never sends, archives or changes anything in your mail or calendar. The only thing it writes is the page's own data.

## What's in here

| | |
|---|---|
| [`page/`](page/) | The page: `index.html` (settings at the top), its photos and the masks behind the living background |
| [`prompt/daily-brief.md`](prompt/daily-brief.md) | The prompt the morning task runs, as a fill-in template |
| [`CLAUDE.md`](CLAUDE.md) | The setup guide Claude follows |
| [`background/`](background/) | How the living background works, how to bring your own photo to life, and the scripts that built the masks |

## Try it first

```sh
cd page && python3 -m http.server
```

Then open http://localhost:8000. Outside Claude the page shows example data (made up), with the background running.

## Make it yours

- **Settings** sit at the top of `page/index.html`: your time zone and location (for sunrise and sunset), the background (`'photos'` or the painted `'ink'` landscapes), and the inbox labels.
- **Your own living photo:** [`background/README.md`](background/README.md) shows how the sheep photo was brought to life and how to do it with yours. Clouds and water work on most landscapes.

## Credits

Built in conversation with Claude by Berend van Nieuwland, who also took the photos. You're welcome to use them in your own brief. The code is MIT licensed.
