# Skill Hub: shared AI agent skills and global rules for Codex, Claude Code, Gemini, and Antigravity

**Skill Hub keeps AI coding agents in sync.** It consolidates personal Agent Skills into one `~/.agents/skills` folder and connects Codex, Claude Code, Gemini CLI, and Antigravity to it. It can also install optional, always-loaded global rules that tell agents to clean up their own temporary files and avoid wasteful commands and token-heavy output. It runs locally on macOS, Linux, and Windows.

| Feature | What it does | Command |
| --- | --- | --- |
| Shared Agent Skills | Merges existing skill folders and links all four agents to one copy | `python3 skill_hub.py install` |
| Disk hygiene rule | Tells agents to remove disposable files they created for a task | `python3 skill_hub.py hygiene-install` |
| Tool and token economy rule | Tells agents to keep commands and output targeted, while allowing necessary large commands | `python3 skill_hub.py economy-install` |

Each feature is optional. The global rules work even if you do not migrate your skills.

## Share skills across AI coding agents

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
for this agent. Consolidate my personal skills for Codex, Claude Code,
Gemini CLI, and Antigravity. Show the plan, stop if names conflict, keep the
backup, and verify the links. Then install and verify the disk hygiene and
tool and token economy global rules.
```

The agent can install the packaged skill with `npx skills add greinald/skill-hub --skill skill-hub -g` or its own skill installer. Its instructions live in `skills/skill-hub/SKILL.md`, with the migration script beside them. Once connected, new skills installed through any covered agent path land in the shared directory.

This repository contains the installer, skill instructions, global rule templates, tests, and documentation. No personal skill files are included.

## Install global AI agent rules for disk and token efficiency

Agent Skills load only when relevant, so they cannot reliably provide an every-task rule. Skill Hub writes managed instruction blocks into the agents' global files: `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, and `~/.gemini/GEMINI.md` (used by Gemini CLI and Antigravity). Install either rule or both:

```sh
python3 skill_hub.py hygiene-install
python3 skill_hub.py economy-install
python3 skill_hub.py hygiene-verify
python3 skill_hub.py economy-verify
```

The [disk hygiene rule](skills/skill-hub/references/disk-hygiene.md) tells agents to track and delete disposable files they create for a task, including intermediate renders and test captures, after preserving requested outputs. It does not direct them to sweep shared temp folders, delete existing user files, or purge app caches and conversation history.

The [tool and token economy rule](skills/skill-hub/references/tool-economy.md) tells agents to use targeted commands and bounded output, avoid repeated scans or tests, and reuse results already obtained. Large commands remain allowed when needed to finish or verify the task. Required checks still take priority over token savings.

The installer preserves other instructions in those files. Re-running an install command updates only its own marked block. Restart running agents to pick up the rules.

On Windows, use `py -3` in place of `python3` in these commands.

To remove either rule without changing the other or your own instructions:

```sh
python3 skill_hub.py hygiene-remove
python3 skill_hub.py economy-remove
```

These rules guide agent behavior. They cannot guarantee cleanup after a crash or force an app to purge its private storage.

### Frequently asked questions

**Does Skill Hub automatically reduce token usage?** The global rule guides agents to make fewer unnecessary tool calls and avoid oversized output. It does not set a token quota or change a model's billing.

**Will disk hygiene delete my project files or AI conversations?** No. The rule is limited to disposable files an agent created for its current task. It explicitly preserves existing files, deliverables, caches shared across tasks, and conversation history.

**Do I need shared skills to use the global rules?** No. The rule commands work independently of skill migration.

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

Skill migration handles user-level skill directories. Project-local skills remain in their projects; built-in and plugin-managed skills remain under their vendors' control. Claude account-synced skills inside `~/.claude/skills/synced` keep their contents and are still managed by Claude. The global rule commands edit only the three instruction files listed above.

This is a filesystem setup tool. It does not make a Claude-specific skill compatible with Codex or Gemini: a shared `SKILL.md` may mention tools that only one agent has. Review a skill's instructions before expecting it to work in every agent. Restart Codex and Claude after installing; Gemini CLI can refresh with `/skills reload`.

Windows uses directory junctions, which do not require Developer Mode or administrator rights. The same backup and restore behavior applies on all three systems. The test suite runs on macOS, Ubuntu, and Windows with Python 3.10 and 3.13 in GitHub Actions.

## Test

```sh
python3 -m unittest discover -s tests -v
```

Tests use temporary home directories. They cover skill migration and restore, plus installing and removing the global rules without erasing existing instructions.

## Why the links work

Codex uses `~/.agents/skills` for user skills. Gemini CLI recognizes both `~/.agents/skills` and `~/.gemini/skills`. Claude Code recognizes skill directories linked from `~/.claude/skills`.

- [Codex skill locations](https://developers.openai.com/api/reference/cli)
- [Gemini CLI skill discovery](https://geminicli.com/docs/cli/skills/)
- [Claude Code linked skills](https://code.claude.com/docs/en/skills)
