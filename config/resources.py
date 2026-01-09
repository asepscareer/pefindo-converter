from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Optional
import httpx

http_client: Optional[httpx.AsyncClient] = None
scheduler: AsyncIOScheduler = None