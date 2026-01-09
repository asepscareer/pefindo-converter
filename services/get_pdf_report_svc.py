import logging
from lxml import etree as ET

logger = logging.getLogger(__name__)
class GetPDFReportSvc:
    
    @staticmethod
    def get_pdf_report_parser_request(xml_data: str) -> str:
        try:
            root = ET.fromstring(xml_data.encode('utf-8'))

            params = root.find('.//cb5:parameters', namespaces=root.nsmap)
            if params is not None: 
                language_code = root.find('.//cus:LanguageCode', namespaces=params.nsmap)
                if language_code is not None:
                    parent = language_code.getparent()
                    reference_code = ET.SubElement(parent, '{http://creditinfo.com/CB5/v5.53/CustomReport}ReferenceCode')
                    reference_code.text = '1234A'
                    parent.insert(parent.index(language_code) + 1, reference_code)

            xml_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_result.replace(b"v5.53", b"v5.109").decode('utf-8')
        except Exception as e:
                logger.error(f"Error parsing XML: {e}")
                return "ERROR"

    @staticmethod
    def get_pdf_report_parser_response(xml_bytes: bytes) -> str:
        try:
            parser = ET.XMLParser(remove_blank_text=True, recover=True)
            root = ET.fromstring(xml_bytes, parser)
            ori_response = root.find(".//{http://creditinfo.com}GetPdfReportResult")
            if (ori_response) is not None:
                return ori_response.text
            else:
                return ""
        except Exception as e:
                logger.error(f"Error parsing XML: {e}")
                return "ERROR"