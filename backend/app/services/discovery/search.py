import logging

from sqlalchemy import or_, select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.services.discovery.query_understanding import QueryUnderstanding
from app.services.ingestion.embedding import EmbeddingClient

logger = logging.getLogger(__name__)


async def hybrid_search(
    db: AsyncSession,
    query: str,
    query_understanding: QueryUnderstanding,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    keyword_results = await _keyword_search(db, query, query_understanding, page, page_size * 2)
    semantic_results = await _semantic_search(db, query, page, page_size * 2)

    merged: dict[str, dict] = {}
    for item in keyword_results:
        slug = item["skill"].slug
        merged[slug] = item

    for item in semantic_results:
        slug = item["skill"].slug
        if slug in merged:
            merged[slug]["semantic_score"] = item["semantic_score"]
        else:
            merged[slug] = item

    all_scores = [v.get("keyword_score", 0) for v in merged.values()] + [
        v.get("semantic_score", 0) for v in merged.values()
    ]
    max_score = max(all_scores) if all_scores else 1.0
    if max_score == 0:
        max_score = 1.0

    for item in merged.values():
        kw = item.get("keyword_score", 0) / max_score
        sem = item.get("semantic_score", 0) / max_score
        item["relevance_score"] = max(kw, sem) if (kw > 0 and sem > 0) else max(kw, sem) * 0.8

    sorted_results = sorted(merged.values(), key=lambda x: x["relevance_score"], reverse=True)
    total = len(sorted_results)
    start = (page - 1) * page_size
    end = start + page_size

    return sorted_results[start:end], total


async def _keyword_search(
    db: AsyncSession,
    query: str,
    qu: QueryUnderstanding,
    page: int,
    limit: int,
) -> list[dict]:
    search_pattern = f"%{query}%"
    conditions = [
        Skill.name.ilike(search_pattern),
        Skill.description.ilike(search_pattern),
    ]

    for tag in qu.tags[:3]:
        conditions.append(Skill.tags.any(text(f"'{tag}'")))
    for cap in qu.capabilities[:3]:
        conditions.append(Skill.capabilities.any(text(f"'{cap}'")))

    q = select(Skill).where(or_(*conditions)).limit(limit)
    result = await db.execute(q)
    skills = result.scalars().all()

    results = []
    for skill in skills:
        score = _compute_keyword_score(skill, query, qu)
        results.append({"skill": skill, "keyword_score": score, "semantic_score": 0.0})
    return results


def _compute_keyword_score(skill: Skill, query: str, qu: QueryUnderstanding) -> float:
    score = 0.0
    q_lower = query.lower()

    if q_lower in skill.name.lower():
        score += 3.0
    elif any(w in skill.name.lower() for w in q_lower.split() if len(w) > 2):
        score += 1.5

    if q_lower in skill.description.lower():
        score += 2.0
    elif any(w in skill.description.lower() for w in q_lower.split() if len(w) > 2):
        score += 1.0

    skill_tags_lower = [t.lower() for t in (skill.tags or [])]
    for tag in qu.tags:
        if tag.lower() in skill_tags_lower:
            score += 1.5

    skill_caps_lower = [c.lower() for c in (skill.capabilities or [])]
    for cap in qu.capabilities:
        if cap.lower() in skill_caps_lower:
            score += 1.0

    return score


async def _semantic_search(
    db: AsyncSession,
    query: str,
    page: int,
    limit: int,
) -> list[dict]:
    embedding_client = EmbeddingClient()
    query_embedding = await embedding_client.embed_text(query)
    if query_embedding is None:
        return []

    try:
        q = (
            select(
                Skill,
                Skill.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .where(Skill.embedding.isnot(None))
            .order_by("distance")
            .limit(limit)
        )
        result = await db.execute(q)
        rows = result.all()

        results = []
        for skill, distance in rows:
            similarity = 1.0 - (distance or 0.0)
            results.append({"skill": skill, "keyword_score": 0.0, "semantic_score": similarity})
        return results
    except Exception as e:
        logger.warning("Semantic search failed: %s", e)
        return []
