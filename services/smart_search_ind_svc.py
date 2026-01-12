from datetime import datetime
import logging
import os
from lxml import etree as ET
from utils import XMLTransformer, generate_reference_code


logger = logging.getLogger(__name__)

class SmartSearchIndSvc:

    @staticmethod
    def _save_daily_record(fullName, dateOfBirth, idNumber, reference_code, status, append=False):
        folder_path = os.path.join("data", "dynamic")
        os.makedirs(folder_path, exist_ok=True)

        today_str = datetime.now().strftime("%d%m%Y")
        file_path = os.path.join(folder_path, f"smart-search-individual-{today_str}.txt")
        file_exists = os.path.exists(file_path)

        mode = "a" if (append and file_exists) else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            if mode == "w" or not file_exists:
                f.write("Full Name,Date Of Birth,ID Number,Reference Code,Status\n")
            f.write(f"{fullName},{dateOfBirth},{idNumber},{reference_code},{status}\n")
        return file_path

    @staticmethod
    def smart_search_individual_parser_request(xml_data: str) -> str:
        try:
            reference_code = generate_reference_code()
            root = ET.fromstring(xml_data.encode('utf-8'))
            
            query = root.find('.//cb5:SmartSearchIndividual', namespaces=root.nsmap)
            if query is not None: 
                params = query.find('.//smar:Parameters', namespaces=query.nsmap)
                if params is not None:
                    parent = params.getparent()
                    ns_url = "http://creditinfo.com/CB5/v5.53/SmartSearch"
                    ref_tag = f"{{{ns_url}}}ReferenceCode"
                    reference_code_element = ET.Element(ref_tag)
                    reference_code_element.text = str(reference_code)
                    parent.insert(parent.index(params) + 1, reference_code_element)

                fullName = XMLTransformer.safe_text(params, './/smar:FullName', namespaces=params.nsmap)
                dateOfBirth = XMLTransformer.safe_text(params, './/smar:DateOfBirth', namespaces=params.nsmap)
                idNumber = XMLTransformer.safe_text(params, './/smar:IdNumber', namespaces=params.nsmap) 
                SmartSearchIndSvc._save_daily_record(fullName, dateOfBirth, idNumber, reference_code, "REQUEST", append=True)
            xml_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_result.replace(b"v5.53", b"v5.109").decode('utf-8')
        except Exception as e:
            logger.error(f"Error parsing Request XML: {e}")
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
            
            idScoreIds = root.xpath(".//a:IdScoreId", namespaces=ns)
            if not idScoreIds:
                return ET.tostring(root, encoding='utf-8').replace(b"v5.109", b"v5.53")

            pefindo_tag = f"{{{ns['a']}}}PefindoId"
            first_id_val = idScoreIds[0].text
            params = root.find('.//a:Parameters', namespaces=ns)
            if params is not None:
                parent_params = params.getparent()
                new_pefindo_params = ET.Element(pefindo_tag)
                new_pefindo_params.text = first_id_val
                parent_params.insert(parent_params.index(params) + 1, new_pefindo_params)

            if len(idScoreIds) > 1:
                second_id_val = idScoreIds[1].text
                records = root.xpath(".//a:SearchIndividualRecord", namespaces=ns)
                
                for rec in records:
                    old_pefindo = rec.find("a:PefindoId", namespaces=ns)
                    if old_pefindo is not None:
                        rec.remove(old_pefindo)
                    
                    ktp_elem = rec.find("a:KTP", namespaces=ns)
                    if ktp_elem is not None:
                        new_rec_pefindo = ET.Element(pefindo_tag)
                        new_rec_pefindo.text = second_id_val
                        ktp_elem.addnext(new_rec_pefindo)

            for ids in idScoreIds:
                p = ids.getparent()
                if p is not None:
                    p.remove(ids)

            xml_bytes_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_bytes_result.replace(b"v5.109", b"v5.53")
        except Exception as e:
            logger.error(f"Error parsing Response XML: {e}")
            return b"ERROR"