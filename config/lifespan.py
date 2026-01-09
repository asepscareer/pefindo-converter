from contextlib import asynccontextmanager
from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import resources
from utils import clean_old_files
import logging
import httpx
import os

logger = logging.getLogger(__name__)

MAX_WORKERS = os.cpu_count()

@asynccontextmanager
async def lifespan(app):
    logger.info("🚀 Inisialisasi Resource...")
    resources.process_pool = ProcessPoolExecutor(max_workers=MAX_WORKERS)
    resources.http_client = httpx.AsyncClient(timeout=120.0)
    
    resources.scheduler = AsyncIOScheduler()
    resources.scheduler.add_job(clean_old_files, "cron", hour=1, minute=0)
    resources.scheduler.start()
    logger.info("🕒 Scheduler started (cleaner @ 01:00 daily)")

    logger.info("✅ Service Ready (Pool, HTTP Client, Scheduler Active)")
    yield

    logger.info("🛑 Cleaning up resources...")
    if resources.scheduler:
        resources.scheduler.shutdown()
        logger.info("🛑 Scheduler stopped")

    if resources.process_pool:
        resources.process_pool.shutdown(wait=True)
        logger.info("🛑 Process pool closed")

    if resources.http_client:
        await resources.http_client.aclose()
        logger.info("🛑 HTTP Client closed")
