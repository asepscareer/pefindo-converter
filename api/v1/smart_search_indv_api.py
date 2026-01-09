import asyncio
from fastapi import APIRouter, Depends, Response, Body
import os
import logging
import utils
from config import resources
from config import settings
from services import SmartSearchIndSvc

SmartSearchIndvRouter = APIRouter()

logger = logging.getLogger(__name__)

# DESTINATION_DOMAIN = settings.destination_domain
DESTINATION_DOMAIN = "http://172.16.90.223:9080/smart-search-individual"

@SmartSearchIndvRouter.post("/smart-search-individual", description="Smart Search Individual endpoint", responses={200: {"content": {"text/xml": {}}}})
async def smart_search_individual(raw_body: str = Body(..., media_type="text/xml"), forward_headers: dict = Depends(utils.get_clean_headers)):
    try:
        logger.info(f"Received request for /smart-search-individual: {raw_body}")
        request_data = SmartSearchIndSvc.smart_search_individual_parser_request(raw_body)
        if (request_data == "ERROR"):
            logger.info(f"Smart Search Individual Request Parsing Error")
            return Response(content="Gateway Error: Smart Search Individual Request Parsing Error", status_code=500)
        logger.info(f"v5.109 Request Data: {request_data}")

        upstream_response = await resources.http_client.post(f"{DESTINATION_DOMAIN}", content=request_data, headers=forward_headers)
        logger.info(f"Upstream Response Content: {upstream_response.content.decode('utf-8')}")

        if upstream_response.status_code == 200:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(resources.process_pool, SmartSearchIndSvc.smart_search_individual_parser_response, upstream_response.content)
            logger.info(f"Successfully processed /smart-search-individual: {response.decode('utf-8')}")
            return Response(content=response, status_code=upstream_response.status_code,media_type="text/xml")
        else:
            logger.info(f"Smart Search Individual Upstream Error: {upstream_response.content}")
            return Response(content=upstream_response.content, status_code=upstream_response.status_code,media_type="text/xml")

    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return Response(content=f"Gateway Error: {str(e)}", status_code=500)