import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.services.ingestion.collector import Collector
from app.services.ingestion.embedding import EmbeddingClient
from app.services.ingestion.enricher import Enricher
from app.services.ingestion.normalizer import normalize_skills
from app.services.security.audit_pipeline import review_skill

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(
        self,
        collector: Collector,
        db_session: AsyncSession,
        enrich_tags: bool = True,
        generate_embeddings: bool = True,
        run_security_audit: bool = True,
    ):
        self._collector = collector
        self._db = db_session
        self._enrich_tags = enrich_tags
        self._generate_embeddings = generate_embeddings
        self._run_security_audit = run_security_audit

    async def run(self) -> dict:
        raw_skills = await self._collector.collect()
        logger.info("Collected %d raw skills", len(raw_skills))

        normalized = normalize_skills(raw_skills)
        logger.info("Normalized to %d unique skills", len(normalized))

        stats = {"collected": len(raw_skills), "normalized": len(normalized), "upserted": 0, "errors": 0}

        for skill_data in normalized:
            try:
                await self._upsert_skill(skill_data)
                stats["upserted"] += 1
            except Exception as e:
                logger.error("Failed to upsert %s: %s", skill_data.get("slug", "?"), e)
                stats["errors"] += 1

        await self._db.commit()
        logger.info("Pipeline complete: %s", stats)
        return stats

    async def _upsert_skill(self, data: dict) -> None:
        slug = data["slug"]

        result = await self._db.execute(select(Skill).where(Skill.slug == slug))
        existing = result.scalar_one_or_none()

        if self._enrich_tags and data.get("content"):
            enricher = Enricher()
            enrichment = await enricher.generate_tags_and_summary(
                data.get("name", ""),
                data.get("description", ""),
                data.get("content", ""),
            )
            if enrichment["tags"] and not data.get("tags"):
                data["tags"] = enrichment["tags"]

        if self._run_security_audit:
            audit = await review_skill(
                name=data.get("name", ""),
                description=data.get("description", ""),
                author=data.get("author", ""),
                tags=data.get("tags", []),
                capabilities=data.get("capabilities", []),
                content=data.get("content", ""),
            )
            data["risk_level"] = audit["risk_level"]
            data["security_score"] = audit["score"]
            data["security_report"] = audit
            data["reviewed_at"] = datetime.now(UTC)
            data["review_version"] = audit.get("review_version", "unknown")

        embedding = None
        if self._generate_embeddings:
            embed_text = f"{data.get('name', '')} {data.get('description', '')} {' '.join(data.get('tags', []))}"
            embedder = EmbeddingClient()
            embedding = await embedder.embed_text(embed_text)

        if existing:
            for key in ("name", "description", "author", "tags", "capabilities",
                        "risk_level", "security_score", "security_report",
                        "content", "version", "registry", "source_url",
                        "install_command", "reviewed_at", "review_version"):
                if key in data:
                    setattr(existing, key, data[key])
            if embedding is not None:
                existing.embedding = embedding
        else:
            skill = Skill(
                name=data.get("name", ""),
                slug=slug,
                description=data.get("description", ""),
                author=data.get("author", ""),
                tags=data.get("tags", []),
                capabilities=data.get("capabilities", []),
                risk_level=data.get("risk_level", "pending"),
                security_score=data.get("security_score", 0),
                security_report=data.get("security_report", {}),
                content=data.get("content"),
                version=data.get("version"),
                registry=data.get("registry"),
                source_url=data.get("source_url"),
                install_command=data.get("install_command"),
                downloads=data.get("downloads", 0),
                stars=data.get("stars", 0),
                embedding=embedding,
                reviewed_at=data.get("reviewed_at"),
                review_version=data.get("review_version"),
            )
            self._db.add(skill)
