from fastapi import FastAPI
from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from middleware_kit import ObservabilityMiddleware, LoggerConfigurator

import uvicorn
import httpx
import os
import logging

from api.v1 import pefindo_router
from helper import resources
from config import clean_old_files
from config import loadenv as env

MAX_WORKERS = os.cpu_count()
LoggerConfigurator().setup()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
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

app = FastAPI(title="Pefindo Transformer", lifespan=lifespan)
app.add_middleware(ObservabilityMiddleware)
app.include_router(pefindo_router, prefix="/pefindo", tags=["Pefindo"])

@app.get("/", description="Root endpoint", tags=["Root"])
async def index():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Pefindo API Integration!"}

@app.get("/health", description="Health check endpoint", tags=["Root"])
async def health_check():
    return {"status": "healthy"}

@app.get("/ready", description="Ready check endpoint", tags=["Root"])
async def ready_check():
    return {"status": "ready"}

if __name__ == "__main__":
    uvicorn.run(app, host=env.HOST, port=env.PORT)