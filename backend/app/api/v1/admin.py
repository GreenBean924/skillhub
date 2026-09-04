"""
Admin endpoints for triggering data ingestion pipelines.
"""
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ingestion.collector import SkillsShCollector
from app.services.ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/ingest/skills-sh")
async def trigger_skills_sh_ingestion(
    background_tasks: BackgroundTasks,
    max_skills: int = 50,
    skip_security_audit: bool = False,
    skip_embeddings: bool = False,
    db: AsyncSession = Depends(get_db),
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

    The pipeline runs in the background to avoid HTTP timeout.
    """
    if max_skills < 1 or max_skills > 200:
        raise HTTPException(status_code=400, detail="max_skills must be between 1 and 200")

    logger.info(
        "Triggering skills.sh ingestion: max_skills=%d, skip_security=%s, skip_embeddings=%s",
        max_skills,
        skip_security_audit,
        skip_embeddings,
    )

    collector = SkillsShCollector(max_skills=max_skills)
    pipeline = IngestionPipeline(
        collector=collector,
        db_session=db,
        enrich_tags=True,
        generate_embeddings=not skip_embeddings,
        run_security_audit=not skip_security_audit,
    )

    async def run_pipeline() -> None:
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
