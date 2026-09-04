"""
Run LLM security review on all skills in the database.

Usage:
    cd backend && PYTHONPATH=. python ../scripts/run_security_review.py
"""

import asyncio
import logging
import sys

from sqlalchemy import select

sys.path.insert(0, "backend")

from app.core.database import async_session_factory
from app.models.skill import Skill
from app.services.security.llm_reviewer import review_skill

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_review():
    async with async_session_factory() as session:
        result = await session.execute(select(Skill))
        skills = result.scalars().all()

        if not skills:
            logger.info("No skills found in database")
            return

        logger.info("Found %d skills to review", len(skills))

        for skill in skills:
            logger.info("Reviewing: %s (%s)", skill.name, skill.slug)

            report = await review_skill(
                name=skill.name,
                description=skill.description,
                author=skill.author,
                tags=skill.tags or [],
                capabilities=skill.capabilities or [],
                content=skill.content or "",
            )

            skill.risk_level = report["risk_level"]
            skill.security_score = report["score"]
            skill.security_report = report

            logger.info(
                "  -> risk=%s, score=%d, findings=%d",
                report["risk_level"],
                report["score"],
                len(report.get("findings", [])),
            )

        await session.commit()
        logger.info("Security review complete. %d skills updated.", len(skills))


if __name__ == "__main__":
    asyncio.run(run_review())
