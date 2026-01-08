from fastapi import Request
from lxml import etree as ET
import logging
from helper import smart_search_data
from .refcode import generate_reference_code


logger = logging.getLogger(__name__)

parser = ET.XMLParser(remove_blank_text=True, recover=True)

def get_clean_headers(request: Request) -> dict:
    headers = dict(request.headers)
    blocked_keys = ["host", "connection", "server", "content-length"]
    
    for key in blocked_keys:
        if key in headers:
            del headers[key]
            
    return headers

def custom_report_parser_response(xml_bytes: bytes) -> bytes:
        ns = {
            's': 'http://schemas.xmlsoap.org/soap/envelope/',
            'a': 'http://creditinfo.com/CB5/v5.109/CustomReport',
            'c': 'http://creditinfo.com/CB5/Common'
        }

        try:
            root = ET.fromstring(xml_bytes, parser)

            # Akses Current Relations
            current_relations = root.find('.//a:CurrentRelations', namespaces=ns)
            if current_relations is not None:
            
            # Ubah tag IdScoreId pada CurrentRelations.RelatedPartyList.RelatedParty[].IdScoreId menjadi CreditinfoId
                related_partyList = current_relations.find('b:RelatedPartyList', namespaces=current_relations.nsmap)
                if related_partyList is not None:
                    for related_party in related_partyList.findall('b:RelatedParty', namespaces=current_relations.nsmap):
                        rel_scoreId = related_party.find('b:IdScoreId', namespaces=current_relations.nsmap)
                        if rel_scoreId is not None:
                            rel_scoreId.tag = f'{{{current_relations.nsmap["b"]}}}CreditinfoId'

            # Ubah tag IdScoreId pada CurrentRelations.ContractRelationList.ContractRelation[].IdScoreId menjadi CreditinfoId
                contract_reasonList = current_relations.find('b:ContractRelationList', namespaces=current_relations.nsmap)
                if contract_reasonList is not None:
                    for contract_relation in contract_reasonList.findall('b:ContractRelation', namespaces=current_relations.nsmap):
                        contract_scoreId = contract_relation.find('b:IdScoreId', namespaces=current_relations.nsmap)
                        if contract_scoreId is not None:
                            contract_scoreId.tag = f'{{{current_relations.nsmap["b"]}}}CreditinfoId'

            # Ubah tag IdScoreId pada CurrentRelations.InvolvementList.Involvement[].IdScoreId menjadi CreditinfoId
                involvement_list = current_relations.find('b:InvolvementList', namespaces=current_relations.nsmap)
                if involvement_list is not None:
                    for involvement in involvement_list.findall('b:Involvement', namespaces=current_relations.nsmap):
                        involvement_scoreId = involvement.find('b:IdScoreId', namespaces=current_relations.nsmap)
                        if involvement_scoreId is not None:
                            involvement_scoreId.tag = f'{{{current_relations.nsmap["b"]}}}CreditinfoId'

            # Akses Dashboard
            dashboard = root.find('.//a:Dashboard', namespaces=ns)
            if dashboard is not None:
                # Hapus tag ClosedContracts dan OpenContracts
                payments_profile = dashboard.find('b:PaymentsProfile', namespaces=dashboard.nsmap)
                if payments_profile is not None:        
                    closed_contracts = payments_profile.find('b:ClosedContracts', namespaces=dashboard.nsmap)
                    open_contracts = payments_profile.find('b:OpenContracts', namespaces=dashboard.nsmap)
                    if closed_contracts is not None:
                        payments_profile.remove(closed_contracts)
                    if open_contracts is not None:
                        payments_profile.remove(open_contracts)

            # Akses Individual
            individual = root.find('.//a:Individual', namespaces=ns)
            if individual is not None:
                # Ubah tag IdScoreId pada Individual.Identifications menjadi PefindoId
                identifications_ind = individual.find('b:Identifications', namespaces =individual.nsmap)
                if identifications_ind is not None:
                    individual_scoreId = identifications_ind.find('b:IdScoreId', namespaces=individual.nsmap)
                    identifications_ind.remove(individual_scoreId)
                    identifications_ind.append(individual_scoreId)
                    if individual_scoreId is not None:
                        individual_scoreId.tag = f'{{{individual.nsmap["b"]}}}PefindoId'

            # Akses Company
            company = root.find('.//a:Company', namespaces=ns)
            if company is not None:
                # Ubah tag IdScoreId pada Company.Identifications menjadi PefindoId
                identifications_com = company.find('b:Identifications', namespaces =company.nsmap)
                if identifications_com is not None:
                    company_scoreId = identifications_com.find('b:IdScoreId', namespaces=company.nsmap)
                    if company_scoreId is not None:
                        company_scoreId.tag = f'{{{company.nsmap["b"]}}}PefindoId'

            # Akses CIP Mengubah tag ReasonsList menjadi ReasonList
            cip = root.find('.//a:CIP', namespaces=ns)
            if cip is not None:
                record_list = cip.find('b:RecordList', namespaces=cip.nsmap)
                if record_list is not None:
                    for record in record_list.findall('b:Record', namespaces=cip.nsmap):
                        reasons_list = record.find('b:ReasonsList', namespaces=cip.nsmap)
                        if reasons_list is not None:
                            reasons_list.tag = f'{{{cip.nsmap["b"]}}}ReasonList'

            # Menambahkan Data pada tag a:Collaterals
            collaterals = dashboard.find('.//a:Collaterals', namespaces=dashboard.nsmap)
            if collaterals is None: 
                ciq = root.find('.//a:CIQ', namespaces=ns)
                parent = ciq.getparent()
                collaterals = ET.Element('{http://creditinfo.com/CB5/v5.109/CustomReport}Collaterals', nsmap={'b': 'http://creditinfo.com/CB5/v5.109/CustomReport/Collaterals'})
                details = ET.SubElement(collaterals, f'{{http://creditinfo.com/CB5/v5.109/CustomReport/Collaterals}}Details')
                collateral = ET.SubElement(details, f'{{http://creditinfo.com/CB5/v5.109/CustomReport/Collaterals}}Collateral')
                fields = ["Description","Insurance","LastUpdate","OwnerName","OwnershipProof","Proportion","SecurityAssignmentType","TaxValue","Type","ValuationDate"]
                for field in fields:
                    elem = ET.SubElement(collateral, f'{{http://creditinfo.com/CB5/v5.109/CustomReport/Collaterals}}{field}')
                    elem.text = ''
                parent.insert(parent.index(ciq) + 1, collaterals)
            
            # Menambahkan Type pada Disputes
            disputes = root.find('.//a:Disputes', namespaces=ns)
            if disputes is not None:
                dispute_list = disputes.find('b:DisputeList', namespaces=disputes.nsmap)
                if dispute_list is None or len(dispute_list) == 0:
                    dispute = dispute_list.find('b:Dispute', namespaces=disputes.nsmap)
                    if dispute is None:
                        dispute = ET.SubElement(dispute_list, f'{{http://creditinfo.com/CB5/v5.109/CustomReport/Disputes}}Dispute')
                        dispute.text = ''
                for i in dispute_list.findall('b:Dispute', namespaces=disputes.nsmap):
                        typE = ET.SubElement(i, f'{{http://creditinfo.com/CB5/v5.109/CustomReport/Disputes}}Type')
                        typE.text = ''

            reportInfo = root.find('.//a:ReportInfo', namespaces=ns)
            if reportInfo is not None:
                report_version = reportInfo.find('b:Version', namespaces=reportInfo.nsmap)
                report_version.text = "553"

            xml_bytes_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_bytes_result.replace(b"v5.109", b"v5.53")
        except Exception as e:
            return "ERROR"

def custom_report_parser_request(xml_data: str) -> str:
    try:
        root = ET.fromstring(xml_data.encode('utf-8'))
        
        query = root.find('.//cb5:GetCustomReport', namespaces=root.nsmap)
        if query is not None: 
            params = root.find('.//cb5:parameters', namespaces=query.nsmap)
            if params is not None:
                inquiry_reason = root.find('.//cus:InquiryReason', namespaces=params.nsmap)
                if inquiry_reason is not None:
                    parent = inquiry_reason.getparent()
                    reference_code = ET.SubElement(parent, '{http://creditinfo.com/CB5/v5.53/CustomReport}ReferenceCode')
                    reference_code.text = f'{generate_reference_code()}'
                    parent.insert(parent.index(inquiry_reason) + 1, reference_code)
            xml_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return xml_result.replace(b"v5.53", b"v5.109").decode('utf-8')
    except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            return "ERROR"

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

        smart_search_data.save_daily_record(fullName, dateOfBirth, idNumber, reference_code, "REQUEST", append=True)
        return xml_result.replace(b"v5.53", b"v5.109").decode('utf-8')
    except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            return "ERROR"

def smart_search_individual_parser_response(xml_bytes: bytes) -> bytes:
        try:
            ns = {
                's': 'http://schemas.xmlsoap.org/soap/envelope/',
                'a': 'http://creditinfo.com/CB5/v5.109/SmartSearch',
                'c': 'http://creditinfo.com/CB5/Common'
            }
            
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

def get_pdf_report_parser_response(xml_bytes: bytes) -> str:
    try: 
        root = ET.fromstring(xml_bytes, parser)
        ori_response = root.find(".//{http://creditinfo.com/CB5/v5.109/CustomReport}GetPdfReportResult")
        if (ori_response) is not None:
            return ori_response.text
        else:
            return ""
    except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            return "ERROR"