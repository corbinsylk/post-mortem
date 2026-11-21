# Post-Mortem

A free Claude Code skill for reels that flopped. Drop in the stats from a reel that flopped, and it finds the exact
second people swiped away, matches it to the line you were saying, and rewrites that part for you. No sign-ups, no API
keys, nothing to pay.

## How to use it

Type `/post-mortem` and send Claude two things:

1. **A screenshot of the reel's retention graph.** In the Instagram app, open the reel, tap **View insights**, and
   scroll to **How long people watched your reel**. Press on the steepest part of the line first, so the exact second
   shows in the little box, then take the screenshot. The whole page is fine, no need to crop.
2. **The reel.** Its link, or the video file if it's a trial reel, a private reel, or the link won't download.

Claude reads the graph, finds where people left (in the hook or anywhere later), transcribes your reel on your own
computer, reads the whole thing to learn how you talk, and opens a one-page report with:

- the graph with the drop-off marked,
- what you were saying at that second,
- why it likely lost people,
- two rewrites of that part in your voice: a close one and a bolder one.

It takes about a minute.

## Install

Paste this into Claude Code:

```
Install the skill from github.com/corbinsylk/post-mortem
```

## What it never does

- It never asks for your Instagram password or logs in.
- It never posts, likes, comments or follows.
- It never invents a number or a line: everything points at your graph or your transcript.
- It never sends your reel anywhere. The transcript is made on your computer.

MIT licence. Made by CreatorPro.
