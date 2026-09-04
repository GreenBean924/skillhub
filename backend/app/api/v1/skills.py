from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.skill import Skill
from app.schemas.skill import (
    FindingResponse,
    InstallResponse,
    MetaResponse,
    QueryUnderstandingResponse,
    RecommendationResponse,
    SearchResponse,
    SecurityReportResponse,
    SkillListResponse,
    SkillResponse,
    StatsResponse,
    TagListResponse,
    TagResponse,
)
from app.services import skill_service
from app.services.discovery.query_understanding import understand_query
from app.services.discovery.search import hybrid_search
from app.services.discovery.ranking import rank_skills
from app.services.recommendation.daily import get_daily_recommendations
from app.models.install_log import InstallLog

router = APIRouter(prefix="/api/v1", tags=["skills"])


def skill_to_response(skill: Skill) -> SkillResponse:
    security_report = skill.security_report or {}
    findings = security_report.get("findings", [])

    return SkillResponse(
        slug=skill.slug,
        name=skill.name,
        author=skill.author,
        description=skill.description,
        tags=skill.tags or [],
        capabilities=skill.capabilities or [],
        security=SecurityReportResponse(
            level=skill.risk_level,
            score=skill.security_score,
            findings=[
                FindingResponse(
                    id=f.get("id", ""),
                    severity=f.get("severity", "info"),
                    title=f.get("title", ""),
                    description=f.get("description", ""),
                    evidence=f.get("evidence"),
                    recommendation=f.get("recommendation", ""),
                )
                for f in findings
            ],
            scannedAt=security_report.get("scannedAt", skill.updated_at.isoformat()),
        ),
        installCommand=skill.install_command or "",
        downloads=skill.downloads,
        stars=skill.stars,
        installCount=skill.install_count,
        version=skill.version,
        createdAt=skill.created_at.isoformat(),
        updatedAt=skill.updated_at.isoformat(),
        content=skill.content,
    )


@router.get("/skills", response_model=SkillListResponse)
async def list_skills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
):
    skills, total = await skill_service.get_skills(db, page, page_size, sort_by, order)
    return SkillListResponse(
        data=[skill_to_response(s) for s in skills],
        meta=MetaResponse(page=page, page_size=page_size, total=total),
    )


@router.get("/skills/search", response_model=SearchResponse)
async def search_skills(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    qu = await understand_query(q)
    results, total = await hybrid_search(db, q, qu, page, page_size)
    results = rank_skills(results)

    response_items = []
    for item in results:
        resp = skill_to_response(item["skill"])
        resp.rankingScore = item.get("ranking_score")
        response_items.append(resp)

    return SearchResponse(
        query_understanding=QueryUnderstandingResponse(tags=qu.tags, capabilities=qu.capabilities),
        data=response_items,
        meta=MetaResponse(page=page, page_size=page_size, total=total),
    )


@router.get("/recommendations", response_model=RecommendationResponse)
async def recommendations(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    recs = await get_daily_recommendations(db, limit)
    return RecommendationResponse(
        data=[skill_to_response(item["skill"]) for item in recs],
    )


@router.get("/skills/{slug}/install", response_model=InstallResponse)
async def install_skill(slug: str, db: AsyncSession = Depends(get_db)):
    skill = await skill_service.get_skill_by_slug(db, slug)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    log = InstallLog(skill_id=skill.id, source="api")
    db.add(log)
    skill.install_count = (skill.install_count or 0) + 1
    await db.commit()

    return InstallResponse(
        slug=skill.slug,
        skill_md=skill.skill_md,
        install_command=skill.install_command or f"skillhub install {skill.slug}",
        risk_level=skill.risk_level,
        security_score=skill.security_score,
        message=f"Installation data for '{skill.name}'",
    )


@router.get("/skills/{slug}", response_model=SkillResponse)
async def get_skill(slug: str, db: AsyncSession = Depends(get_db)):
    skill = await skill_service.get_skill_by_slug(db, slug)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill_to_response(skill)


@router.get("/tags", response_model=TagListResponse)
async def list_tags(db: AsyncSession = Depends(get_db)):
    tags_data = await skill_service.get_tags(db)
    return TagListResponse(data=[TagResponse(name=t["name"], count=t["count"]) for t in tags_data])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    stats = await skill_service.get_stats(db)
    return StatsResponse(**stats)
