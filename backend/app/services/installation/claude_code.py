import shutil
from pathlib import Path

from app.services.installation.adapter import (
    AgentAdapter,
    AgentType,
    EnvironmentInfo,
    InstallationResult,
)

SKILL_DIR = Path.home() / ".claude" / "skills"


class ClaudeCodeAdapter(AgentAdapter):
    async def detect_environment(self) -> EnvironmentInfo:
        claude_dir = Path.home() / ".claude"
        detected = claude_dir.exists()
        return EnvironmentInfo(
            agent_type=AgentType.CLAUDE_CODE,
            detected=detected,
            install_dir=SKILL_DIR if detected else None,
        )

    async def install_skill(self, slug: str, skill_md: str) -> InstallationResult:
        skill_dir = SKILL_DIR / slug
        try:
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "CLAUDE.md").write_text(skill_md, encoding="utf-8")
            return InstallationResult(
                success=True,
                slug=slug,
                agent_type=AgentType.CLAUDE_CODE,
                install_dir=skill_dir,
                message=f"Skill '{slug}' installed to {skill_dir}",
            )
        except OSError as e:
            return InstallationResult(
                success=False,
                slug=slug,
                agent_type=AgentType.CLAUDE_CODE,
                error=str(e),
                message=f"Failed to install '{slug}': {e}",
            )

    async def uninstall_skill(self, slug: str) -> bool:
        skill_dir = SKILL_DIR / slug
        if not skill_dir.exists():
            return False
        shutil.rmtree(skill_dir)
        return True

    async def list_skills(self) -> list[str]:
        if not SKILL_DIR.exists():
            return []
        return [d.name for d in SKILL_DIR.iterdir() if d.is_dir()]

    async def verify_installation(self, slug: str) -> bool:
        skill_dir = SKILL_DIR / slug
        claude_md = skill_dir / "CLAUDE.md"
        return skill_dir.exists() and claude_md.exists()
