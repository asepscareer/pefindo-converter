import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Response, Body
import os
import logging
import helper
from helper import resources
from config import loadenv as config

app = APIRouter()

logger = logging.getLogger(__name__)

DESTINATION_DOMAIN = config.DESTINATION_DOMAIN
MAX_WORKERS = os.cpu_count()

@app.post("/v1/get-custom-report", description="Get Custom Report endpoint", responses={200: {"content": {"text/xml": {}}}}, tags=["Pefindo"])
async def custom_report(raw_body: str = Body(..., media_type="text/xml"), forward_headers: dict = Depends(helper.get_clean_headers)):
    try:
        logger.info(f"Received request for /get-custom-report: {raw_body}")
        request_data = helper.custom_report_parser_request(raw_body)
        if (request_data == "ERROR"):
            logger.info(f"❌ Custom Report Request Parsing Error")
            return Response(content="Gateway Error: Custom Report Request Parsing Error", status_code=500)
        logger.info(f"v5.109 Request Data: {request_data}")

        upstream_response = await resources.http_client.post(f"{DESTINATION_DOMAIN}", content=request_data, headers=forward_headers)
        if upstream_response.status_code == 200:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(resources.process_pool, helper.custom_report_parser_response, upstream_response.content)
            logger.info("Successfully processed /get-custom-report request")
            return Response(content=response, status_code=upstream_response.status_code,media_type="text/xml")
        else:
            logger.info(f"❌ Custom Report Upstream Error: {upstream_response.content}")
            return Response(content=upstream_response.content, status_code=upstream_response.status_code,media_type="text/xml")

    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return Response(content=f"Gateway Error: {str(e)}", status_code=500)

@app.post("/v1/smart-search-individual", description="Smart Search Individual endpoint", responses={200: {"content": {"text/xml": {}}}})
async def smart_search_individual(raw_body: str = Body(..., media_type="text/xml"), forward_headers: dict = Depends(helper.get_clean_headers)):
    try:
        logger.info(f"Received request for /smart-search-individual: {raw_body}")
        request_data = helper.smart_search_individual_parser_request(raw_body)
        if (request_data == "ERROR"):
            logger.info(f"❌ Smart Search Individual Request Parsing Error")
            return Response(content="Gateway Error: Smart Search Individual Request Parsing Error", status_code=500)
        logger.info(f"v5.109 Request Data: {request_data}")

        upstream_response = await resources.http_client.post(f"{DESTINATION_DOMAIN}", content=request_data, headers=forward_headers)
        logger.info(f"Upstream Response Content: {upstream_response.content.decode('utf-8')}")

        if upstream_response.status_code == 200:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(resources.process_pool, helper.smart_search_individual_parser_response, upstream_response.content)
            logger.info(f"Successfully processed /smart-search-individual: {response}")
            return Response(content=response, status_code=upstream_response.status_code,media_type="text/xml")
        else:
            logger.info(f"❌ Smart Search Individual Upstream Error: {upstream_response.content}")
            return Response(content=upstream_response.content, status_code=upstream_response.status_code,media_type="text/xml")

    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return Response(content=f"Gateway Error: {str(e)}", status_code=500)
    

@app.post("/v1/get-pdf-report", description="Get PDF Report endpoint", responses={200: {"content": {"text/xml": {}}}})
async def get_pdf_report(raw_body: str = Body(..., media_type="text/xml"), forward_headers: dict = Depends(helper.get_clean_headers)):
    try:
        logger.info(f"Received request for /get-pdf-report: {raw_body}")
        request_data = helper.get_pdf_report_parser_request(raw_body)
        if (request_data == "ERROR"):
            logger.info(f"❌ Get PDF Report Request Parsing Error")
            return Response(content="Gateway Error: Get PDF Report Request Parsing Error", status_code=500)
        logger.info(f"v5.109 Request Data: {request_data}")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        XML_TEMPLATE_PATH = os.path.join(BASE_DIR, '..', 'template', 'response', 'get_pdf_report.xml')

        upstream_response = await resources.http_client.post(f"{DESTINATION_DOMAIN}", content=request_data, headers=forward_headers)
        logger.info(f"Upstream Response Content: {upstream_response.content.decode('utf-8')}")
        if upstream_response.status_code == 200:
            loop = asyncio.get_running_loop()
            string_base64 = await loop.run_in_executor(resources.process_pool, helper.get_pdf_report_parser_response, upstream_response.content)
            logger.info(f"Successfully parsed data")
            if string_base64 != 'ERROR':
                with open(XML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                    xml_content = f.read()
                final_xml = xml_content.format(string_base64=string_base64)
                logger.info(f"Successfully processed /get-pdf-report: {final_xml}")
                return Response(content=final_xml, status_code=upstream_response.status_code, media_type="text/xml")
            else:
                logger.info(f"❌ Get PDF Report Upstream Error: {upstream_response.content}")
                return Response(content=upstream_response.content, status_code=upstream_response.status_code,media_type="text/xml")
        else:
            logger.info(f"❌ Get PDF Report Upstream Error: {upstream_response.content}")
            return Response(content=upstream_response.content, status_code=upstream_response.status_code,media_type="text/xml")

    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return Response(content=f"Gateway Error: {str(e)}", status_code=500)
    

@app.post("/v1/get-other-report", description="Get Other Report endpoint", responses={200: {"content": {"text/xml": {}}}})
async def get_other_report(raw_body: str = Body(..., media_type="text/xml"), forward_headers: dict = Depends(helper.get_clean_headers)):
    try:
        logger.info(f"Received request for /get-other-report: {raw_body}")
        now_obj = datetime.now(timezone.utc)
        expired_obj = now_obj + timedelta(minutes=5)

        created_at = now_obj.isoformat(timespec='milliseconds').replace("+00:00", "Z")
        expired_at = expired_obj.isoformat(timespec='milliseconds').replace("+00:00", "Z")

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'template', 'response', 'get_other_report.xml'), "r", encoding="utf-8") as f:
            xml_template = f.read()
        final_xml = xml_template.format(created_at=created_at, expired_at=expired_at)
        logger.info(f"Successfully processed /get-other-report: {final_xml}")
        return Response(content=final_xml, status_code=200, media_type="text/xml")
    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return Response(content=f"Gateway Error: {str(e)}", status_code=500)