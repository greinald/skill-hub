import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/skill-hub/scripts"))
from skill_hub import install, plan, restore, verify


def skill(path: Path, name: str, body: str = "Shared instructions") -> None:
    directory = path / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test\n---\n{body}\n",
        encoding="utf-8",
    )


class SkillHubTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
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
        shared = self.home / ".agents/skills/alpha/SKILL.md"
        self.assertTrue(shared.samefile(codex / "alpha/SKILL.md"))
        self.assertTrue(shared.samefile(claude / "alpha/SKILL.md"))
        self.assertTrue(shared.samefile(gemini / "alpha/SKILL.md"))
        skill(claude, "new-skill")
        self.assertTrue((self.home / ".agents/skills/new-skill/SKILL.md").exists())
        self.assertTrue((codex / "new-skill/SKILL.md").exists())
        self.assertIsNone(install(self.home))
        restore(self.home, backup)
        self.assertFalse(codex.is_symlink())
        self.assertFalse(claude.is_symlink())
        self.assertFalse(gemini.is_symlink())
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
        root.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "links elsewhere"):
            plan(self.home)


if __name__ == "__main__":
    unittest.main()
