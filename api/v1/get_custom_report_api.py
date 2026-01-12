import asyncio
from fastapi import APIRouter, Depends, Response, Body
import logging
from config import settings
import utils
from services import GetCustomReportSvc
from config import resources

GetCustomReportRouter = APIRouter()

logger = logging.getLogger(__name__)

# DESTINATION_DOMAIN = settings.destination_domain
DESTINATION_DOMAIN = "http://172.16.90.223:9080/get-custom-report"

@GetCustomReportRouter.post("/get-custom-report", description="Get Custom Report endpoint", responses={200: {"content": {"text/xml": {}}}}, tags=["Pefindo"])
async def custom_report(raw_body: str = Body(..., media_type="text/xml"), forward_headers: dict = Depends(utils.get_clean_headers)):
    try:
        logger.info(f"Received request for /get-custom-report: {raw_body}")
        request_data = GetCustomReportSvc.custom_report_parser_request(raw_body)
        if (request_data == "ERROR"):
            logger.info(f"Custom Report Request Parsing Error")
            return Response(content="Gateway Error: Custom Report Request Parsing Error", status_code=500)
        logger.info(f"v5.109 Request Data: {request_data}")

        upstream_response = await resources.http_client.post(f"{DESTINATION_DOMAIN}", content=request_data, headers=forward_headers, timeout=120.0)
        if upstream_response.status_code == 200:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(resources.process_pool, GetCustomReportSvc.custom_report_parser_response, upstream_response.content)
            logger.info("Successfully processed /get-custom-report request")
            return Response(content=response, status_code=upstream_response.status_code,media_type="text/xml")
        else:
            logger.info(f"Custom Report Upstream Error: {upstream_response.content}")
            return Response(content=upstream_response.content, status_code=upstream_response.status_code,media_type="text/xml")

    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return Response(content=f"Gateway Error: {str(e)}", status_code=500)