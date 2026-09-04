"""
Admin endpoints for triggering data ingestion pipelines.
"""
import logging
import secrets

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from app.core.config import get_settings
from app.core.database import async_session_factory
from app.services.ingestion.collector import SkillsShCollector
from app.services.ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

settings = get_settings()


async def require_admin(x_admin_key: str = Header(default="")) -> None:
    """
    Gate admin endpoints behind an API key (AGENTS.md §6.4).

    Fails closed: if ADMIN_API_KEY is unset, access is denied in production.
    In development an unset key is allowed so local usage stays frictionless.
    """
    configured = settings.ADMIN_API_KEY
    if configured:
        if not secrets.compare_digest(x_admin_key, configured):
            raise HTTPException(status_code=403, detail="Invalid admin key")
        return

    if settings.ENVIRONMENT == "production":
        logger.error("Admin endpoint called but ADMIN_API_KEY is not configured")
        raise HTTPException(status_code=403, detail="Admin access is not configured")

    logger.warning("ADMIN_API_KEY not set; allowing admin access in development")


@router.post("/ingest/skills-sh", dependencies=[Depends(require_admin)])
async def trigger_skills_sh_ingestion(
    background_tasks: BackgroundTasks,
    max_skills: int = 50,
    skip_security_audit: bool = False,
    skip_embeddings: bool = False,
) -> dict:
    """
    Trigger ingestion of skills from skills.sh.

    This runs the full ingestion pipeline:
    1. Scrape skills.sh listing page
    2. Fetch detail for each skill
    3. Fetch SKILL.md content from GitHub
    4. Normalize and upsert into database
    5. Run security audit (optional)
    6. Generate embeddings (optional)

    The pipeline runs in the background to avoid HTTP timeout, using its own
    database session because the request-scoped session closes on return.
    """
    if max_skills < 1 or max_skills > 200:
        raise HTTPException(status_code=400, detail="max_skills must be between 1 and 200")

    logger.info(
        "Triggering skills.sh ingestion: max_skills=%d, skip_security=%s, skip_embeddings=%s",
        max_skills,
        skip_security_audit,
        skip_embeddings,
    )

    async def run_pipeline() -> None:
        async with async_session_factory() as session:
            collector = SkillsShCollector(max_skills=max_skills)
            pipeline = IngestionPipeline(
                collector=collector,
                db_session=session,
                enrich_tags=True,
                generate_embeddings=not skip_embeddings,
                run_security_audit=not skip_security_audit,
            )
            try:
                stats = await pipeline.run()
                logger.info("Ingestion pipeline completed: %s", stats)
            except Exception as e:
                logger.error("Ingestion pipeline failed: %s", e)

    background_tasks.add_task(run_pipeline)

    return {
        "message": "Ingestion pipeline started in background",
        "params": {
            "max_skills": max_skills,
            "skip_security_audit": skip_security_audit,
            "skip_embeddings": skip_embeddings,
        },
    }
