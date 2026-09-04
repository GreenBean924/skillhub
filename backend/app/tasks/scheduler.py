import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_daily_ingestion():
    from app.core.database import async_session_factory
    from app.services.ingestion.collector import SeedDataCollector
    from app.services.ingestion.pipeline import IngestionPipeline
    from scripts.seed_data import MOCK_SKILLS

    logger.info("Starting daily ingestion job")
    async with async_session_factory() as session:
        collector = SeedDataCollector(MOCK_SKILLS)
        pipeline = IngestionPipeline(collector=collector, db_session=session)
        stats = await pipeline.run()
    logger.info("Daily ingestion complete: %s", stats)


def setup_scheduler():
    scheduler.add_job(
        run_daily_ingestion,
        trigger="cron",
        hour=2,
        minute=0,
        id="daily_ingestion",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — daily ingestion at 02:00")
