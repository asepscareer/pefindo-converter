from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Response, Body
import os
import logging
import utils
from config import settings

GetOtherReportRouter = APIRouter()

logger = logging.getLogger(__name__)

# DESTINATION_DOMAIN = settings.destination_domain
DESTINATION_DOMAIN = "http://172.16.90.223:9080/get-other-report"

@GetOtherReportRouter.post("/get-other-report", description="Get Other Report endpoint", responses={200: {"content": {"text/xml": {}}}})
async def get_other_report(raw_body: str = Body(..., media_type="text/xml"), forward_headers: dict = Depends(utils.get_clean_headers)):
    try:
        logger.info(f"Received request for /get-other-report: {raw_body}")
        now_obj = datetime.now(timezone.utc)
        expired_obj = now_obj + timedelta(minutes=5)

        created_at = now_obj.isoformat(timespec='milliseconds').replace("+00:00", "Z")
        expired_at = expired_obj.isoformat(timespec='milliseconds').replace("+00:00", "Z")

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'template', 'response', 'get_other_report.xml'), "r", encoding="utf-8") as f:
            xml_template = f.read()
        final_xml = xml_template.format(created_at=created_at, expired_at=expired_at)
        logger.info(f"Successfully processed /get-other-report: {final_xml}")
        return Response(content=final_xml, status_code=200, media_type="text/xml")
    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return Response(content=f"Gateway Error: {str(e)}", status_code=500)