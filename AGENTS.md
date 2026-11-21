# Post-Mortem

This repo holds a free Claude Code skill: `/post-mortem`, in `.claude/skills/post-mortem/`.
Its instructions are in that folder's `SKILL.md`.

## When the user asks to install it

(For example, "Install the skill from github.com/corbinsylk/post-mortem".) Do this without explaining the steps:

1. Clone the repo into a temporary folder: `git clone --depth 1 https://github.com/corbinsylk/post-mortem`. If git is
   missing, download https://github.com/corbinsylk/post-mortem/archive/refs/heads/main.zip and unzip it instead.
2. Copy its `.claude/skills/post-mortem` folder to the user's personal skills folder, replacing any older copy:
   - Mac or Linux: `~/.claude/skills/post-mortem`
   - Windows: `%USERPROFILE%\.claude\skills\post-mortem`
   Leave their `Documents/Post-Mortem` folder alone: it holds their past post-mortems.
3. Run `python3 tools/doctor.py` from the installed folder. Install anything it lists (on a Mac: `brew install yt-dlp
   ffmpeg whisper-cpp`, then `python3 tools/doctor.py --get-model`). Tell them in plain words what you're installing
   and why ("the free transcriber, so your reel is read on your own computer"). Run it again until it says READY.
4. Tell them: "Done. Type /post-mortem. It works best in the Claude desktop app. If it doesn't show, start a
   new chat."

An update is the same steps; the copy replaces the old one.

## When this folder itself is open

The skill already works here. If the user wants it in every folder, do the install above.

## Working on the skill

Tests: `python3 -m unittest discover -s tests -v`. The tools are standard-library Python; keep them that way.
