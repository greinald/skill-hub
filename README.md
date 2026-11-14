# Skill Hub

Keep your personal Agent Skills in one folder while Codex, Claude Code, and Gemini continue using their usual skill paths.

```text
~/.codex/skills ───────────────┐
~/.claude/skills ──────────────┤
~/.gemini/skills ──────────────┼──→ ~/.agents/skills
~/.gemini/config/skills ───────┤
~/.gemini/antigravity/skills ──┘
```

The installer moves each tool's **original directory into a dated backup**, copies its entries into the shared directory, and replaces the original directory with a symbolic link. A new skill installed through any linked path then lands in the same shared directory. It does not download, publish, or modify the contents of your skills.

## Install

Requires macOS or Linux and Python 3.10 or newer. Clone this repository, then run:

```sh
git clone https://github.com/greinald/skill-hub.git
cd skill-hub
python3 skill_hub.py plan
python3 skill_hub.py install
python3 skill_hub.py verify
```

The repository is currently private, so cloning requires access to it. No personal skill files are included in this repository.

`plan` checks for name collisions and shows what will be copied before anything changes. If two directories contain different entries with the same name, installation stops and names both paths. Resolve the conflict yourself; Skill Hub never chooses a version silently.

The install command prints the backup path. Keep it until you have restarted your agents and confirmed their skill lists. Running `install` again is safe and reports that the links are already installed.

## Restore

Use the backup path printed during installation:

```sh
python3 skill_hub.py restore --backup ~/.agents/skill-hub-backups/YYYYMMDD-HHMMSS-XXXXXXXX
```

This restores the original tool directories. The shared directory remains in place for manual review, so skills created after installation are not deleted.

## What this covers

This handles user-level skill directories. Project-local skills remain in their projects; built-in and plugin-managed skills remain under their vendors' control. Claude account-synced skills inside `~/.claude/skills/synced` keep their contents and are still managed by Claude.

This is a filesystem setup tool. It does not make a Claude-specific skill compatible with Codex or Gemini: a shared `SKILL.md` may mention tools that only one agent has. Review a skill's instructions before expecting it to work in every agent. Restart Codex and Claude after installing; Gemini CLI can refresh with `/skills reload`.

The current version is for macOS and Linux. Windows needs a separate implementation because creating directory links has different permissions and behavior.

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
