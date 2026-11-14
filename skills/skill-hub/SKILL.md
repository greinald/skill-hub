---
name: skill-hub
description: Consolidate existing personal Agent Skills for Codex, Claude Code, and Gemini into one shared folder. Use when a user asks to set up, inspect, verify, or undo a shared skills directory across these agents.
---

# Skill Hub

Help the user keep one copy of each personal skill at `~/.agents/skills`. This skill handles **migration of existing folders**. For installing or updating individual skills afterward, use the agent's normal installer or the [Skills CLI](https://github.com/vercel-labs/skills).

The migration script is [scripts/skill_hub.py](scripts/skill_hub.py), relative to this `SKILL.md`. Run it with Python 3.10 or newer on macOS, Linux, or Windows. Use `python3` where available, or `py -3` on Windows. Do not guess the installed path; locate this skill folder first.

## Set up

1. Run `python3 scripts/skill_hub.py plan` from this skill folder and read every collision it reports. The plan makes no changes.
2. If two different entries have the same name, stop and show both paths to the user. Do not overwrite either or silently choose one.
3. When the user has asked to set up shared skills, run `python3 scripts/skill_hub.py install` (or `py -3 ...` on Windows). It copies entries into the shared folder, moves each original tool folder to a dated backup, and creates symlinks on macOS/Linux or directory junctions on Windows. Keep the printed backup path.
4. Run `python3 scripts/skill_hub.py verify`. Confirm the expected links resolve to the same shared directory.
5. Tell the user where the backup is and that running agents may need a restart or skill reload.

The script is idempotent. It covers `~/.codex/skills`, `~/.claude/skills`, `~/.gemini/skills`, `~/.gemini/config/skills`, and `~/.gemini/antigravity/skills`. It does not move project-local skills or vendor plugin caches.

## Inspect or undo

- For a status request, run `python3 scripts/skill_hub.py verify`.
- For an undo request, use the backup path from setup: `python3 scripts/skill_hub.py restore --backup <path>`. The shared directory remains afterward so newly created skills are not deleted.

These are filesystem links. A skill may still contain instructions or tools specific to one agent; sharing its files does not make that workflow portable.
