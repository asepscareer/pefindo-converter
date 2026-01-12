import logging
from lxml import etree as ET
from utils import generate_reference_code

logger = logging.getLogger(__name__)

class GetPDFReportSvc:
    
    @staticmethod
    def get_pdf_report_parser_request(xml_data: str) -> str:
        try:
            root = ET.fromstring(xml_data.encode('utf-8'))

            params = root.find('.//cb5:parameters', namespaces=root.nsmap)
            if params is not None: 
                language_code = params.find('.//cus:LanguageCode', namespaces=params.nsmap)
                if language_code is not None:
                    parent = language_code.getparent()
                    
                    ns_url = "http://creditinfo.com/CB5/v5.53/CustomReport"
                    ref_code_tag = f"{{{ns_url}}}ReferenceCode"
                    
                    if parent.find(ref_code_tag) is None:
                        new_ref_elem = ET.Element(ref_code_tag)
                        new_ref_elem.text = generate_reference_code()
                        
                        idx = parent.index(language_code)
                        parent.insert(idx + 1, new_ref_elem)

            xml_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_result.replace(b"v5.53", b"v5.109").decode('utf-8')
        except Exception as e:
            logger.error(f"Error parsing GetPDFReport Request: {e}")
            return "ERROR"

    @staticmethod
    def get_pdf_report_parser_response(xml_bytes: bytes) -> str:
        try:
            parser = ET.XMLParser(remove_blank_text=True, recover=True)
            root = ET.fromstring(xml_bytes, parser)
            ori_response = root.xpath("//*[local-name()='GetPdfReportResult']")
            if ori_response:
                return ori_response[0].text if ori_response[0].text else ""
            return ""
        except Exception as e:
            logger.error(f"Error parsing GetPDFReport Response: {e}")
            return "ERROR"