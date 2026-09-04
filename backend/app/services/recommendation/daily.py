from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.services.discovery.ranking import compute_ranking_score


async def get_daily_recommendations(
    db: AsyncSession,
    limit: int = 10,
) -> list[dict]:
    query = select(Skill).where(Skill.risk_level.in_(["safe", "low", "medium"])).limit(100)
    result = await db.execute(query)
    skills = result.scalars().all()

    scored = []
    for skill in skills:
        trending = skill.trending_score or 0.0
        rec_score = compute_ranking_score(skill, relevance_score=trending)

        if skill.risk_level == "safe":
            rec_score += 0.05
        elif skill.risk_level == "low":
            rec_score += 0.02

        rec_score = min(1.0, rec_score)
        scored.append({"skill": skill, "ranking_score": round(rec_score, 4)})

    scored.sort(key=lambda x: x["ranking_score"], reverse=True)
    return scored[:limit]
