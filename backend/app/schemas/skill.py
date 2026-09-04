from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FindingResponse(BaseModel):
    id: str
    severity: str
    title: str
    description: str
    evidence: str | None = None
    recommendation: str


class SecurityReportResponse(BaseModel):
    level: str
    score: int
    findings: list[FindingResponse]
    scannedAt: str


class SkillResponse(BaseModel):
    slug: str
    name: str
    author: str
    description: str
    tags: list[str]
    capabilities: list[str]
    security: SecurityReportResponse
    installCommand: str
    downloads: int
    stars: int
    installCount: int = 0
    version: str | None = None
    createdAt: str
    updatedAt: str
    content: str | None = None
    rankingScore: float | None = None

    model_config = {"from_attributes": True}


class MetaResponse(BaseModel):
    page: int
    page_size: int
    total: int


class SkillListResponse(BaseModel):
    data: list[SkillResponse]
    meta: MetaResponse


class TagResponse(BaseModel):
    name: str
    count: int


class TagListResponse(BaseModel):
    data: list[TagResponse]


class StatsResponse(BaseModel):
    total_skills: int
    safe_skills: int
    total_downloads: int
    last_updated: str | None = None


class QueryUnderstandingResponse(BaseModel):
    tags: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query_understanding: QueryUnderstandingResponse
    data: list[SkillResponse]
    meta: MetaResponse


class RecommendationResponse(BaseModel):
    data: list[SkillResponse]


class InstallResponse(BaseModel):
    slug: str
    skill_md: str | None
    install_command: str
    risk_level: str
    security_score: int
    agent_type: str = "claude_code"
    message: str
