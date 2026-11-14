#!/usr/bin/env python3
"""Share user-installed Agent Skills across Codex, Claude Code, and Gemini."""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4


ROOTS = (
    ".codex/skills",
    ".claude/skills",
    ".gemini/skills",
    ".gemini/config/skills",
    ".gemini/antigravity/skills",
)
IGNORED = {".DS_Store"}


def is_junction(path: Path) -> bool:
    if os.name != "nt":
        return False
    try:
        return path.lstat().st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT
    except (FileNotFoundError, AttributeError):
        return False


def is_directory_link(path: Path) -> bool:
    return path.is_symlink() or is_junction(path)


def create_directory_link(link: Path, target: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd.exe", "/d", "/v:off", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise OSError(
                f"mklink failed for {link}: "
                f"{result.stdout.strip()} {result.stderr.strip()}"
            )
        if not is_junction(link) or link.resolve() != target.resolve():
            if is_junction(link):
                link.rmdir()
            raise OSError(f"Failed to create a junction from {link} to {target}")
    else:
        link.symlink_to(target, target_is_directory=True)


def remove_directory_link(link: Path) -> None:
    if is_junction(link):
        link.rmdir()
    else:
        link.unlink()


def same_tree(left: Path, right: Path) -> bool:
    if is_directory_link(left) or is_directory_link(right):
        return same_tree(left.resolve(strict=True), right.resolve(strict=True))
    if left.is_dir() != right.is_dir():
        return False
    if left.is_file():
        return filecmp.cmp(left, right, shallow=False)
    left_names = {p.name for p in left.iterdir() if p.name not in IGNORED}
    right_names = {p.name for p in right.iterdir() if p.name not in IGNORED}
    return left_names == right_names and all(
        same_tree(left / name, right / name) for name in left_names
    )


def paths(home: Path) -> tuple[Path, list[Path]]:
    return home / ".agents" / "skills", [home / root for root in ROOTS]


def plan(home: Path) -> tuple[Path, list[Path], list[tuple[Path, Path]]]:
    hub, roots = paths(home)
    if is_directory_link(hub) or (hub.exists() and not hub.is_dir()):
        raise ValueError(f"Shared path must be a real directory: {hub}")
    additions: list[tuple[Path, Path]] = []
    candidates: dict[str, Path] = {
        child.name: child for child in hub.iterdir()
    } if hub.exists() else {}
    for root in roots:
        if is_directory_link(root):
            if root.resolve(strict=True) != hub.resolve():
                raise ValueError(f"Skill path already links elsewhere: {root}")
            continue
        if root.exists() and not root.is_dir():
            raise ValueError(f"Skill path is not a directory: {root}")
        if not root.exists():
            continue
        for entry in root.iterdir():
            if entry.name in IGNORED:
                continue
            previous = candidates.get(entry.name)
            if previous is None:
                candidates[entry.name] = entry
                additions.append((entry, hub / entry.name))
            elif not same_tree(entry, previous):
                raise ValueError(
                    f"Conflicting entries named {entry.name!r}:\n"
                    f"  {previous}\n  {entry}\n"
                    "Resolve this collision before installing; no files were changed."
                )
    return hub, roots, additions


def install(home: Path) -> Path | None:
    hub, roots, additions = plan(home)
    pending = [root for root in roots if not is_directory_link(root)]
    if not pending and not additions:
        print(f"Already installed: {hub}")
        return None

    backup = home / ".agents" / "skill-hub-backups" / (
        datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]
    )
    backup.mkdir(parents=True)
    hub_created = not hub.exists()
    hub.mkdir(parents=True, exist_ok=True)
    added: list[Path] = []
    moved: list[tuple[Path, Path]] = []
    linked: list[Path] = []
    try:
        for source, target in additions:
            added.append(target)
            if is_directory_link(source):
                resolved = source.resolve(strict=True)
                if resolved.is_dir():
                    create_directory_link(target, resolved)
                else:
                    shutil.copy2(resolved, target)
            elif source.is_dir():
                shutil.copytree(source, target, symlinks=True)
            else:
                shutil.copy2(source, target)

        for root in pending:
            root.parent.mkdir(parents=True, exist_ok=True)
            if root.exists():
                archived = backup / root.relative_to(home)
                archived.parent.mkdir(parents=True, exist_ok=True)
                root.rename(archived)
                moved.append((root, archived))
            create_directory_link(root, hub)
            linked.append(root)

        manifest = {
            "version": 1,
            "hub": str(hub),
            "roots": [
                {"path": str(root), "had_directory": any(root == old for old, _ in moved)}
                for root in pending
            ],
            "added": [str(path) for path in added],
        }
        (backup / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
    except Exception:
        for root in reversed(linked):
            if is_directory_link(root):
                remove_directory_link(root)
        for root, archived in reversed(moved):
            archived.rename(root)
        for target in reversed(added):
            if is_directory_link(target):
                remove_directory_link(target)
            elif target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
        if hub_created and not any(hub.iterdir()):
            hub.rmdir()
        raise

    print(f"Shared skills: {hub}")
    for root in roots:
        print(f"  {root} -> {hub}")
    print(f"Original folders saved at: {backup}")
    return backup


def verify(home: Path) -> bool:
    hub, roots = paths(home)
    if not hub.is_dir() or is_directory_link(hub):
        print(f"Missing real shared directory: {hub}")
        return False
    okay = True
    for root in roots:
        valid = is_directory_link(root) and root.resolve() == hub.resolve()
        print(f"{'OK' if valid else 'FAIL'}  {root}")
        okay = okay and valid
    print(f"Direct skill folders: {sum((p / 'SKILL.md').is_file() for p in hub.iterdir())}")
    return okay


def restore(home: Path, backup: Path) -> None:
    backup = backup.resolve(strict=True)
    expected_parent = (home / ".agents" / "skill-hub-backups").resolve()
    if backup.parent != expected_parent:
        raise ValueError(f"Backup must be directly under {expected_parent}")
    manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    hub, allowed_roots = paths(home)
    if manifest["hub"] != str(hub):
        raise ValueError("Backup belongs to a different home directory")
    recorded_roots = [Path(item["path"]) for item in manifest["roots"]]
    if len(set(recorded_roots)) != len(recorded_roots) or not set(recorded_roots) <= set(allowed_roots):
        raise ValueError("Backup lists an unexpected skill path")
    for item in manifest["roots"]:
        root = Path(item["path"])
        if not is_directory_link(root) or root.resolve() != hub.resolve():
            raise ValueError(f"Expected shared link, found something else: {root}")
        if item["had_directory"] and not (backup / root.relative_to(home)).is_dir():
            raise ValueError(f"Original folder missing from backup: {root}")
    for item in manifest["roots"]:
        root = Path(item["path"])
        remove_directory_link(root)
        if item["had_directory"]:
            (backup / root.relative_to(home)).rename(root)
        print(f"Restored {root}")
    print(f"Shared files remain at {hub}; remove them manually after review.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("plan", "install", "verify", "restore")
    )
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    parser.add_argument("--backup", type=Path, help="Backup path printed by install")
    args = parser.parse_args()
    try:
        if args.command == "plan":
            hub, roots, additions = plan(args.home)
            print(f"Shared directory: {hub}")
            print(f"Paths to link: {sum(not is_directory_link(p) for p in roots)}")
            print(f"Entries to copy: {len(additions)}")
            for source, target in additions:
                print(f"  {source} -> {target}")
        elif args.command == "install":
            install(args.home)
        elif args.command == "verify":
            return 0 if verify(args.home) else 1
        else:
            if args.backup is None:
                parser.error("restore requires --backup")
            restore(args.home, args.backup)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
