from fastapi import Request
from lxml import etree as ET
import logging

logger = logging.getLogger(__name__)
def get_clean_headers(request: Request) -> dict:
    headers = dict(request.headers)
    blocked_keys = ["host", "connection", "server", "content-length"]
    
    for key in blocked_keys:
        if key in headers:
            del headers[key]
            
    return headers