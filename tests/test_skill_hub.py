import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/skill-hub/scripts"))
from skill_hub import (
    create_directory_link,
    hygiene_install,
    hygiene_remove,
    hygiene_verify,
    install,
    is_directory_link,
    is_junction,
    plan,
    policy_install,
    policy_remove,
    policy_verify,
    remove_directory_link,
    restore,
    verify,
)


def skill(path: Path, name: str, body: str = "Shared instructions") -> None:
    directory = path / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test\n---\n{body}\n",
        encoding="utf-8",
    )


class SkillHubTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="skill hub test ")
        self.home = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_install_shares_one_file_and_restores_originals(self) -> None:
        codex = self.home / ".codex/skills"
        claude = self.home / ".claude/skills"
        gemini = self.home / ".gemini/skills"
        skill(codex, "alpha")
        skill(claude, "beta")
        skill(gemini, "alpha")
        backup = install(self.home)
        self.assertIsNotNone(backup)
        self.assertTrue(verify(self.home))
        if os.name == "nt":
            self.assertTrue(is_junction(codex))
        else:
            self.assertTrue(codex.is_symlink())
        shared = self.home / ".agents/skills/alpha/SKILL.md"
        self.assertTrue(shared.samefile(codex / "alpha/SKILL.md"))
        self.assertTrue(shared.samefile(claude / "alpha/SKILL.md"))
        self.assertTrue(shared.samefile(gemini / "alpha/SKILL.md"))
        skill(claude, "new-skill")
        self.assertTrue((self.home / ".agents/skills/new-skill/SKILL.md").exists())
        self.assertTrue((codex / "new-skill/SKILL.md").exists())
        self.assertIsNone(install(self.home))
        restore(self.home, backup)
        self.assertFalse(is_directory_link(codex))
        self.assertFalse(is_directory_link(claude))
        self.assertFalse(is_directory_link(gemini))
        self.assertTrue((codex / "alpha/SKILL.md").exists())
        self.assertTrue((claude / "beta/SKILL.md").exists())
        self.assertTrue((gemini / "alpha/SKILL.md").exists())

    def test_conflict_stops_before_changes(self) -> None:
        codex = self.home / ".codex/skills"
        claude = self.home / ".claude/skills"
        skill(codex, "same", "Version one")
        skill(claude, "same", "Version two")
        with self.assertRaisesRegex(ValueError, "Conflicting entries"):
            plan(self.home)
        self.assertFalse((self.home / ".agents").exists())
        self.assertFalse(codex.is_symlink())
        self.assertFalse(claude.is_symlink())

    def test_refuses_unrelated_existing_link(self) -> None:
        target = self.home / "unrelated"
        target.mkdir()
        root = self.home / ".claude/skills"
        root.parent.mkdir()
        create_directory_link(root, target)
        try:
            with self.assertRaisesRegex(ValueError, "links elsewhere"):
                plan(self.home)
        finally:
            remove_directory_link(root)

    def test_hygiene_installs_preserves_existing_and_removes_its_block(self) -> None:
        codex = self.home / ".codex/AGENTS.md"
        codex.parent.mkdir(parents=True)
        codex.write_text("# My existing rules\nKeep this rule.\n", encoding="utf-8")

        hygiene_install(self.home)
        self.assertTrue(hygiene_verify(self.home))
        self.assertIn("Keep this rule.", codex.read_text(encoding="utf-8"))
        for relative in (".codex/AGENTS.md", ".claude/CLAUDE.md", ".gemini/GEMINI.md"):
            self.assertIn("Delete only files you created for this task", (self.home / relative).read_text())

        first = codex.read_text(encoding="utf-8")
        hygiene_install(self.home)
        self.assertEqual(codex.read_text(encoding="utf-8"), first)

        hygiene_remove(self.home)
        self.assertFalse(hygiene_verify(self.home))
        self.assertIn("Keep this rule.", codex.read_text(encoding="utf-8"))
        self.assertFalse((self.home / ".claude/CLAUDE.md").exists())
        self.assertFalse((self.home / ".gemini/GEMINI.md").exists())

    def test_hygiene_refuses_partial_marker_without_changing_any_file(self) -> None:
        codex = self.home / ".codex/AGENTS.md"
        codex.parent.mkdir(parents=True)
        codex.write_text("<!-- skill-hub:disk-hygiene:start -->\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Malformed disk hygiene block"):
            hygiene_install(self.home)
        self.assertFalse((self.home / ".claude/CLAUDE.md").exists())

    def test_tool_economy_installs_and_removes_independently(self) -> None:
        hygiene_install(self.home)
        policy_install(self.home, "tool-economy")
        self.assertTrue(policy_verify(self.home, "tool-economy"))
        self.assertTrue(hygiene_verify(self.home))

        codex = self.home / ".codex/AGENTS.md"
        first = codex.read_text(encoding="utf-8")
        self.assertIn("Run a large or expensive command", first)
        policy_install(self.home, "tool-economy")
        self.assertEqual(codex.read_text(encoding="utf-8"), first)

        policy_remove(self.home, "tool-economy")
        self.assertFalse(policy_verify(self.home, "tool-economy"))
        self.assertTrue(hygiene_verify(self.home))
        self.assertNotIn("Run a large or expensive command", codex.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
