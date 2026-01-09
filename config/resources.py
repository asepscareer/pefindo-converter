from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Optional
import httpx

process_pool: Optional[ProcessPoolExecutor] = None
http_client: Optional[httpx.AsyncClient] = None
scheduler: AsyncIOScheduler = None