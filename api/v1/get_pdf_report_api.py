import asyncio
from fastapi import APIRouter, Depends, Response, Body
import os
import logging
from services import GetPDFReportSvc
from config import resources
from config import settings
import utils

GetPdfReportRouter = APIRouter()

logger = logging.getLogger(__name__)

# DESTINATION_DOMAIN = settings.destination_domain
DESTINATION_DOMAIN = "http://172.16.90.223:9080/get-pdf-report"

@GetPdfReportRouter.post("/get-pdf-report", description="Get PDF Report endpoint", responses={200: {"content": {"text/xml": {}}}})
async def get_pdf_report(raw_body: str = Body(..., media_type="text/xml"), forward_headers: dict = Depends(utils.get_clean_headers)):
    try:
        logger.info(f"Received request for /get-pdf-report: {raw_body}")
        request_data = GetPDFReportSvc.get_pdf_report_parser_request(raw_body)
        if (request_data == "ERROR"):
            logger.info(f"Get PDF Report Request Parsing Error")
            return Response(content="Gateway Error: Get PDF Report Request Parsing Error", status_code=500)
        logger.info(f"v5.109 Request Data: {request_data}")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        XML_TEMPLATE_PATH = os.path.join(BASE_DIR, '..', '..', 'template', 'response', 'get_pdf_report.xml')

        upstream_response = await resources.http_client.post(f"{DESTINATION_DOMAIN}", content=request_data, headers=forward_headers, timeout=120.0)
        logger.info(f"Upstream Response Content: {upstream_response.content.decode('utf-8')}")
        if upstream_response.status_code == 200:
            loop = asyncio.get_running_loop()
            string_base64 = await loop.run_in_executor(resources.process_pool, GetPDFReportSvc.get_pdf_report_parser_response, upstream_response.content)
            logger.info(f"Successfully parsed data")
            if string_base64 != 'ERROR':
                with open(XML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                    xml_content = f.read()
                final_xml = xml_content.format(string_base64=string_base64)
                logger.info(f"Successfully processed /get-pdf-report: {final_xml}")
                return Response(content=final_xml, status_code=upstream_response.status_code, media_type="text/xml")
            else:
                logger.info(f"Get PDF Report Upstream Error: {upstream_response.content}")
                return Response(content=upstream_response.content, status_code=upstream_response.status_code,media_type="text/xml")
        else:
            logger.info(f"Get PDF Report Upstream Error: {upstream_response.content}")
            return Response(content=upstream_response.content, status_code=upstream_response.status_code,media_type="text/xml")

    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return Response(content=f"Gateway Error: {str(e)}", status_code=500)