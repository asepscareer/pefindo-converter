from datetime import datetime
import logging
import os
from lxml import etree as ET

from utils import generate_reference_code


logger = logging.getLogger(__name__)

class SmartSearchIndSvc:

    @staticmethod
    def _save_daily_record(fullName, dateOfBirth, idNumber, reference_code, status, append=False):
        folder_path = os.path.join("data", "dynamic")
        os.makedirs(folder_path, exist_ok=True)

        today_str = datetime.now().strftime("%d%m%Y")
        file_name = f"smart-search-individual-{today_str}.txt"
        file_path = os.path.join(folder_path, file_name)

        header = "Full Name,Date Of Birth,ID Number,Reference Code,Status\n"
        file_exists = os.path.exists(file_path)
        mode = "a" if append and file_exists else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            if not file_exists:
                f.write(header)
            if not append:
                f.write(header)
            f.write(f"{fullName},{dateOfBirth},{idNumber},{reference_code},{status}\n")
        return file_path

    @staticmethod
    def smart_search_individual_parser_request(xml_data: str) -> str:
        try:
            reference_code = generate_reference_code()
            root = ET.fromstring(xml_data.encode('utf-8'))
            
            query = root.find('.//cb5:SmartSearchIndividual', namespaces=root.nsmap)
            if query is not None: 
                params = root.find('.//smar:Parameters', namespaces=query.nsmap)
                if params is not None:
                    parent = params.getparent()
                    reference_code_element = ET.SubElement(parent, '{http://creditinfo.com/CB5/v5.53/SmartSearch}ReferenceCode')
                    reference_code_element.text = f'{reference_code}'
                    parent.insert(parent.index(params) + 1, reference_code_element)
            xml_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)

            fullName = params.find('.//smar:FullName', namespaces=params.nsmap).text if params.find('.//smar:FullName', namespaces=params.nsmap) is not None else ""
            dateOfBirth = params.find('.//smar:DateOfBirth', namespaces=params.nsmap).text if params.find('.//smar:DateOfBirth', namespaces=params.nsmap) is not None else ""
            idNumber = params.find('.//smar:IdNumber', namespaces=params.nsmap).text if params.find('.//smar:IdNumber', namespaces=params.nsmap) is not None else ""
            logger.info(f"Invidual Reuqest Info : Name={fullName}, DOB={dateOfBirth}, NIK={idNumber}, ReferenceCode={reference_code}")

            SmartSearchIndSvc._save_daily_record(fullName, dateOfBirth, idNumber, reference_code, "REQUEST", append=True)
            return xml_result.replace(b"v5.53", b"v5.109").decode('utf-8')
        except Exception as e:
                logger.error(f"Error parsing XML: {e}")
                return "ERROR"

    @staticmethod
    def smart_search_individual_parser_response(xml_bytes: bytes) -> bytes:
        try:
            
            ns = {
                    's': 'http://schemas.xmlsoap.org/soap/envelope/',
                    'a': 'http://creditinfo.com/CB5/v5.109/SmartSearch',
                    'c': 'http://creditinfo.com/CB5/Common'
                }
                
            parser = ET.XMLParser(remove_blank_text=True, recover=True)
            root = ET.fromstring(xml_bytes, parser)
            idScoreId = root.xpath("//a:IdScoreId", namespaces=ns)
            ns_url = idScoreId[0].nsmap.get("a")
            pefindoId = f"{{{ns_url}}}PefindoId"
            for i in idScoreId: i.tag = pefindoId

            for idx, i in enumerate(idScoreId):
                if (idx == 0):
                    params = root.find('.//a:Parameters', namespaces=ns)
                    if params is not None:
                        parent = params.getparent()
                        pefindoId = ET.Element('{http://creditinfo.com/CB5/v5.109/SmartSearch}PefindoId')
                        pefindoId.text = i.text
                        parent.insert(parent.index(params) + 1, pefindoId)
                    i.getparent().remove(i)
                elif (idx == 1):
                    searchIndividualRecord = root.xpath("//a:SearchIndividualRecord", namespaces=ns)
                    if searchIndividualRecord is not None:
                        for idx2, i in enumerate(searchIndividualRecord):
                            search_pefindoId = i.find(".//a:PefindoId", namespaces=searchIndividualRecord[idx2].nsmap)
                            if search_pefindoId is not None:
                                i.remove(search_pefindoId)
                                params = i.find('.//a:KTP', namespaces=ns)
                                parent = params.getparent()
                                pefindoId = ET.Element('{http://creditinfo.com/CB5/v5.109/SmartSearch}PefindoId')
                                pefindoId.text = search_pefindoId.text
                                parent.insert(parent.index(params) + 1, pefindoId)
            xml_bytes_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_bytes_result.replace(b"v5.109", b"v5.53")
        except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            return "ERROR"