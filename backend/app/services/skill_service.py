from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.skill import Skill


async def get_skills(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
) -> tuple[list[Skill], int]:
    order_col = getattr(Skill, sort_by, Skill.created_at)
    if order == "desc":
        order_col = order_col.desc()
    else:
        order_col = order_col.asc()

    count_query = select(func.count(Skill.id))
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    query = select(Skill).order_by(order_col).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    skills = result.scalars().all()

    return list(skills), total


async def get_skill_by_slug(db: AsyncSession, slug: str) -> Skill | None:
    query = select(Skill).where(Skill.slug == slug)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def search_skills(
    db: AsyncSession,
    query: str,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Skill], int]:
    search_pattern = f"%{query}%"

    count_query = select(func.count(Skill.id)).where(
        (Skill.name.ilike(search_pattern))
        | (Skill.description.ilike(search_pattern))
        | (Skill.tags.any(text(f"'{query}'")))
        | (Skill.capabilities.any(text(f"'{query}'")))
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    skill_query = (
        select(Skill)
        .where(
            (Skill.name.ilike(search_pattern))
            | (Skill.description.ilike(search_pattern))
            | (Skill.tags.any(text(f"'{query}'")))
            | (Skill.capabilities.any(text(f"'{query}'")))
        )
        .order_by(Skill.stars.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(skill_query)
    skills = result.scalars().all()

    return list(skills), total


async def get_tags(db: AsyncSession) -> list[dict[str, int]]:
    query = select(Skill.tags).where(Skill.tags.isnot(None))
    result = await db.execute(query)
    all_tags = result.scalars().all()

    tag_counts: dict[str, int] = {}
    for tags in all_tags:
        if tags:
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return [{"name": name, "count": count} for name, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)]


async def get_stats(db: AsyncSession) -> dict:
    count_query = select(func.count(Skill.id))
    count_result = await db.execute(count_query)
    total_skills = count_result.scalar() or 0

    safe_query = select(func.count(Skill.id)).where(Skill.risk_level == "safe")
    safe_result = await db.execute(safe_query)
    safe_skills = safe_result.scalar() or 0

    downloads_query = select(func.sum(Skill.downloads))
    downloads_result = await db.execute(downloads_query)
    total_downloads = downloads_result.scalar() or 0

    updated_query = select(func.max(Skill.updated_at))
    updated_result = await db.execute(updated_query)
    last_updated = updated_result.scalar()

    return {
        "total_skills": total_skills,
        "safe_skills": safe_skills,
        "total_downloads": total_downloads,
        "last_updated": last_updated.isoformat() if last_updated else None,
    }
