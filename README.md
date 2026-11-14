# Skill Hub: one shared skills folder for Codex, Claude Code, and Gemini

Stop managing separate copies of your AI agent skills. **Skill Hub consolidates existing personal Agent Skills into `~/.agents/skills` and connects Codex, Claude Code, Gemini CLI, and Gemini Antigravity to that folder.** Install it as an Agent Skill and ask your agent to do the migration, or run the Python script yourself on Windows, macOS, or Linux.

## The problem it solves

Each coding agent can save skills in its own directory. After using several agents, the same skill may be copied into multiple folders, while other skills are visible to only one agent. Updating a skill in one place then leaves the other copies stale.

Skill Hub gives those user-level directories one shared destination. **A skill added through a connected agent path appears through the others without making another active copy.** The migration saves your original directories in a dated backup, checks for conflicting names before changing anything, and provides a restore command.

```text
~/.codex/skills ───────────────┐
~/.claude/skills ──────────────┤
~/.gemini/skills ──────────────┼──→ ~/.agents/skills
~/.gemini/config/skills ───────┤
~/.gemini/antigravity/skills ──┘
```

On macOS and Linux, the connections are symlinks. On Windows, they are directory junctions. The [Skills CLI](https://github.com/vercel-labs/skills) already supports canonical installs for new skills; Skill Hub focuses on bringing **existing scattered skill folders** together. It does not upload or publish your skills.

## Install with your AI agent

In Codex, Claude Code, or Gemini, paste:

```text
Install the skill-hub Agent Skill from https://github.com/greinald/skill-hub
for this agent, then use it to consolidate my personal skills for Codex,
Claude Code, and Gemini. Show me the plan, stop if names conflict, keep the
backup, and verify the links.
```

The agent can install the packaged skill with `npx skills add greinald/skill-hub --skill skill-hub -g` or its own skill installer. Its instructions live in `skills/skill-hub/SKILL.md`, with the migration script beside them. Once connected, new skills installed through any covered agent path land in the shared directory.

This repository contains only the installer, skill instructions, tests, and documentation. No personal skill files are included.

## Install manually

Requires Python 3.10 or newer. On macOS or Linux:

```sh
git clone https://github.com/greinald/skill-hub.git
cd skill-hub
python3 skill_hub.py plan
python3 skill_hub.py install
python3 skill_hub.py verify
```

On Windows in PowerShell:

```powershell
git clone https://github.com/greinald/skill-hub.git
cd skill-hub
py -3 skill_hub.py plan
py -3 skill_hub.py install
py -3 skill_hub.py verify
```

`plan` checks for name collisions and shows what will be copied before anything changes. If two directories contain different entries with the same name, installation stops and names both paths. Resolve the conflict yourself; Skill Hub never chooses a version silently. The install command prints the backup path. Keep it until you have restarted your agents and confirmed their skill lists. Running `install` again is safe.

## Restore

Use the backup path printed during installation:

```sh
python3 skill_hub.py restore --backup ~/.agents/skill-hub-backups/YYYYMMDD-HHMMSS-XXXXXXXX
```

This restores the original tool directories. The shared directory remains in place for manual review, so skills created after installation are not deleted.

## What this covers

This handles user-level skill directories. Project-local skills remain in their projects; built-in and plugin-managed skills remain under their vendors' control. Claude account-synced skills inside `~/.claude/skills/synced` keep their contents and are still managed by Claude.

This is a filesystem setup tool. It does not make a Claude-specific skill compatible with Codex or Gemini: a shared `SKILL.md` may mention tools that only one agent has. Review a skill's instructions before expecting it to work in every agent. Restart Codex and Claude after installing; Gemini CLI can refresh with `/skills reload`.

Windows uses directory junctions, which do not require Developer Mode or administrator rights. The same backup and restore behavior applies on all three systems. The test suite runs on macOS, Ubuntu, and Windows with Python 3.10 and 3.13 in GitHub Actions.

## Test

```sh
python3 -m unittest discover -s tests -v
```

Tests use temporary home directories. They cover merging unique skills, preserving matching copies, blocking conflicts before changes, sharing a newly installed skill, repeated installation, and restoring originals.

## Why the links work

Codex uses `~/.agents/skills` for user skills. Gemini CLI recognizes both `~/.agents/skills` and `~/.gemini/skills`. Claude Code recognizes skill directories linked from `~/.claude/skills`.

- [Codex skill locations](https://developers.openai.com/api/reference/cli)
- [Gemini CLI skill discovery](https://geminicli.com/docs/cli/skills/)
- [Claude Code linked skills](https://code.claude.com/docs/en/skills)
