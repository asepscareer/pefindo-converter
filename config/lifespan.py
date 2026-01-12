from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
import multiprocessing
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import resources
from utils import clean_old_files
import logging
import httpx

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    logger.info("🚀 Inisialisasi Resource...")
    resources.http_client = httpx.AsyncClient(timeout=120.0)
    cpu_count = multiprocessing.cpu_count()
    resources.process_pool = ProcessPoolExecutor(max_workers=min(cpu_count, 4))
    
    logger.info(f"🔧 Process pool created with {min(cpu_count, 4)} workers")
    resources.scheduler = AsyncIOScheduler()
    resources.scheduler.add_job(clean_old_files, "cron", hour=1, minute=0, max_instances=1, coalesce=True)
    resources.scheduler.start()
    logger.info("🕒 Scheduler started (cleaner @ 01:00 daily)")

    logger.info("✅ Service Ready (HTTP Client, Scheduler Active)")
    yield

    logger.info("🛑 Cleaning up resources...")
    if resources.scheduler:
        resources.scheduler.shutdown()
        logger.info("🛑 Scheduler stopped")

    if resources.http_client:
        await resources.http_client.aclose()
        logger.info("🛑 HTTP Client closed")
