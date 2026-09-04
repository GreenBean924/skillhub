import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from typer.testing import CliRunner

from skillhub_cli.main import app
from skillhub_cli.api import SkillHubAPI

runner = CliRunner()


MOCK_SKILL = {
    "slug": "test-skill",
    "name": "Test Skill",
    "author": "Tester",
    "description": "A test skill",
    "tags": ["python"],
    "capabilities": ["file_read"],
    "security": {"level": "safe", "score": 95, "findings": [], "scannedAt": "2026-09-01T00:00:00"},
    "installCommand": "skillhub install test-skill",
    "downloads": 100,
    "stars": 10,
    "version": "1.0.0",
}

MOCK_INSTALL = {
    "slug": "test-skill",
    "skill_md": "# Test Skill\nA test skill for testing.",
    "install_command": "skillhub install test-skill",
    "risk_level": "safe",
    "security_score": 95,
    "agent_type": "claude_code",
    "message": "Installation data for 'Test Skill'",
}


class TestVersionCommand:
    def test_version(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout


class TestInstallCommand:
    @patch("skillhub_cli.main.SkillHubAPI")
    def test_install_dry_run(self, mock_api_cls, tmp_path):
        mock_api = MagicMock()
        mock_api.get_skill.return_value = MOCK_SKILL
        mock_api_cls.return_value = mock_api

        result = runner.invoke(app, ["install", "test-skill", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.stdout

    @patch("skillhub_cli.main.SkillHubAPI")
    def test_install_safe_skill(self, mock_api_cls, tmp_path):
        mock_api = MagicMock()
        mock_api.get_skill.return_value = MOCK_SKILL
        mock_api.install_skill.return_value = MOCK_INSTALL
        mock_api_cls.return_value = mock_api

        with patch("skillhub_cli.main.SKILL_DIR", tmp_path / "skills"):
            result = runner.invoke(app, ["install", "test-skill"])
        assert result.exit_code == 0
        assert "installed successfully" in result.stdout

    @patch("skillhub_cli.main.SkillHubAPI")
    def test_install_high_risk_requires_confirmation(self, mock_api_cls, tmp_path):
        high_risk_skill = {**MOCK_SKILL, "security": {"level": "high", "score": 30, "findings": [], "scannedAt": "2026-09-01T00:00:00"}}
        mock_api = MagicMock()
        mock_api.get_skill.return_value = high_risk_skill
        mock_api_cls.return_value = mock_api

        result = runner.invoke(app, ["install", "test-skill"], input="n\n")
        assert result.exit_code == 0
        assert "cancelled" in result.stdout

    @patch("skillhub_cli.main.SkillHubAPI")
    def test_install_not_found(self, mock_api_cls):
        mock_api = MagicMock()
        mock_api.get_skill.side_effect = Exception("404 Not Found")
        mock_api_cls.return_value = mock_api

        result = runner.invoke(app, ["install", "nonexistent"])
        assert result.exit_code == 1


class TestUninstallCommand:
    def test_uninstall_not_installed(self, tmp_path):
        with patch("skillhub_cli.main.SKILL_DIR", tmp_path / "empty"):
            result = runner.invoke(app, ["uninstall", "nonexistent"])
        assert result.exit_code == 1
        assert "not installed" in result.stdout

    def test_uninstall_dry_run(self, tmp_path):
        skill_dir = tmp_path / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "CLAUDE.md").write_text("test")

        with patch("skillhub_cli.main.SKILL_DIR", tmp_path / "skills"):
            result = runner.invoke(app, ["uninstall", "test-skill", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.stdout

    def test_uninstall_existing(self, tmp_path):
        skill_dir = tmp_path / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "CLAUDE.md").write_text("test")

        with patch("skillhub_cli.main.SKILL_DIR", tmp_path / "skills"):
            result = runner.invoke(app, ["uninstall", "test-skill"])
        assert result.exit_code == 0
        assert "Uninstalled" in result.stdout
        assert not skill_dir.exists()


class TestListCommand:
    def test_list_empty(self, tmp_path):
        with patch("skillhub_cli.main.SKILL_DIR", tmp_path / "empty"):
            result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No skills installed" in result.stdout

    def test_list_with_skills(self, tmp_path):
        skill_dir = tmp_path / "skills"
        (skill_dir / "alpha").mkdir(parents=True)
        (skill_dir / "beta").mkdir(parents=True)

        with patch("skillhub_cli.main.SKILL_DIR", skill_dir):
            result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "alpha" in result.stdout
        assert "beta" in result.stdout


class TestSearchCommand:
    @patch("skillhub_cli.main.SkillHubAPI")
    def test_search_with_results(self, mock_api_cls):
        mock_api = MagicMock()
        mock_api.search_skills.return_value = {
            "data": [MOCK_SKILL],
            "meta": {"total": 1, "page": 1, "page_size": 20},
        }
        mock_api_cls.return_value = mock_api

        result = runner.invoke(app, ["search", "test"])
        assert result.exit_code == 0
        assert "Test Skill" in result.stdout

    @patch("skillhub_cli.main.SkillHubAPI")
    def test_search_no_results(self, mock_api_cls):
        mock_api = MagicMock()
        mock_api.search_skills.return_value = {"data": [], "meta": {"total": 0, "page": 1, "page_size": 20}}
        mock_api_cls.return_value = mock_api

        result = runner.invoke(app, ["search", "nonexistent"])
        assert result.exit_code == 0
        assert "No skills found" in result.stdout


class TestAuditCommand:
    @patch("skillhub_cli.main.SkillHubAPI")
    def test_audit_shows_report(self, mock_api_cls):
        mock_api = MagicMock()
        mock_api.get_skill.return_value = MOCK_SKILL
        mock_api_cls.return_value = mock_api

        result = runner.invoke(app, ["audit", "test-skill"])
        assert result.exit_code == 0
        assert "Test Skill" in result.stdout
        assert "safe" in result.stdout.lower() or "SAFE" in result.stdout
