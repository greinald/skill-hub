---
name: skill-hub
description: Merge scattered personal Agent Skills for Codex, Claude Code, and Gemini into one shared folder, so skills stay in sync without duplicate copies. Use for setup, verification, or restore on Windows, macOS, and Linux.
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

## Always-on agent rules

Shared skills load only when selected. To give every task a temporary-file cleanup rule, run `python3 scripts/skill_hub.py hygiene-install`. This adds the same managed block to Codex's `~/.codex/AGENTS.md`, Claude Code's `~/.claude/CLAUDE.md`, and Gemini CLI and Antigravity's `~/.gemini/GEMINI.md`. It preserves instructions outside the block and is safe to rerun.

Run `python3 scripts/skill_hub.py hygiene-verify` to check all three files, or `hygiene-remove` to remove only Skill Hub's block. The rule is in [references/disk-hygiene.md](references/disk-hygiene.md). It directs agents to remove their own disposable task files while preserving deliverables and existing data. Running agents may need a restart to load the new rule.

For targeted commands and lower tool-output token use, run `python3 scripts/skill_hub.py economy-install`, then `economy-verify`. This installs [references/tool-economy.md](references/tool-economy.md) into the same global files as a separate managed block. `economy-remove` removes that block without changing disk hygiene or other instructions. Large commands remain appropriate when the task requires them.

## Inspect or undo

- For a status request, run `python3 scripts/skill_hub.py verify`.
- For an undo request, use the backup path from setup: `python3 scripts/skill_hub.py restore --backup <path>`. The shared directory remains afterward so newly created skills are not deleted.

These are filesystem links. A skill may still contain instructions or tools specific to one agent; sharing its files does not make that workflow portable.
