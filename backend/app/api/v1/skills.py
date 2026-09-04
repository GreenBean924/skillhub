from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.skill import Skill
from app.schemas.skill import (
    FindingResponse,
    MetaResponse,
    QueryUnderstandingResponse,
    SearchResponse,
    SecurityReportResponse,
    SkillListResponse,
    SkillResponse,
    StatsResponse,
    TagListResponse,
    TagResponse,
)
from app.services import skill_service

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
    skills, total = await skill_service.search_skills(db, q, page, page_size)
    return SearchResponse(
        query_understanding=QueryUnderstandingResponse(tags=[], capabilities=[]),
        data=[skill_to_response(s) for s in skills],
        meta=MetaResponse(page=page, page_size=page_size, total=total),
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
