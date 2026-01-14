import logging
from lxml import etree as ET

from utils import generate_reference_code
from mappings.reference_fields import REFERENCE_FIELDS
from mappings.target_fields import SECTION_TARGET_FIELDS

logger = logging.getLogger(__name__)

class GetCustomReportSvc:

    @staticmethod
    def custom_report_parser_response(xml_bytes: bytes) -> bytes:
        ns = {
            's': 'http://schemas.xmlsoap.org/soap/envelope/',
            'a': 'http://creditinfo.com/CB5/v5.109/CustomReport',
            'c': 'http://creditinfo.com/CB5/Common'
        }

        def _remapping_response_value(node, ns: dict, ref_mapping, target_fields):
            for field_name in target_fields:
                child_node = node.find(f'b:{field_name}', namespaces=ns)
                if child_node is None:
                    child_node = node.find(f'c:{field_name}', namespaces=ns)
                if child_node is not None and child_node.text:
                    original_val = child_node.text
                    new_val = ref_mapping.get(field_name, {}).get(original_val, original_val)
                    child_node.text = new_val
            return root

        try:
            parser = ET.XMLParser(remove_blank_text=True, recover=True)
            root = ET.fromstring(xml_bytes, parser)

            # Akses Current Relations
            def current_relations_section_mapping(root, ns):
                current_relations = root.find('.//a:CurrentRelations', namespaces=ns)
                if current_relations is not None:
                    # Ubah tag IdScoreId pada CurrentRelations.RelatedPartyList.RelatedParty[].IdScoreId menjadi CreditinfoId
                        related_partyList = current_relations.find('b:RelatedPartyList', namespaces=current_relations.nsmap)
                        if related_partyList is not None:
                            for related_party in related_partyList.findall('b:RelatedParty', namespaces=current_relations.nsmap):
                                rel_scoreId = related_party.find('b:IdScoreId', namespaces=current_relations.nsmap)
                                if rel_scoreId is not None:
                                    rel_scoreId.tag = f'{{{current_relations.nsmap["b"]}}}CreditinfoId'

                                # RelatedParty
                                related_party_ref_mapping = {
                                    "Gender": REFERENCE_FIELDS["Gender"],
                                    "IDNumberType": REFERENCE_FIELDS["IDNumberType"],
                                    "SubjectStatus": REFERENCE_FIELDS["SubjectStatus"],
                                    "SubjectType" : REFERENCE_FIELDS["SubjectType"],
                                    "TypeOfRelation": REFERENCE_FIELDS["TypeOfRelation"]
                                }
                                _remapping_response_value(node=related_party, ns=related_party.nsmap, ref_mapping=related_party_ref_mapping, target_fields=SECTION_TARGET_FIELDS["CurrentRelations"]["RelatedParty"])

                                # RelatedParty MainAddress
                                main_address_node = related_party.find('b:MainAddress', namespaces=current_relations.nsmap)
                                if main_address_node is not None:
                                    mainaddress_ref_mapping = {
                                        "City": REFERENCE_FIELDS["City"],
                                        "Country": REFERENCE_FIELDS["Country"],
                                    }
                                    _remapping_response_value(node=main_address_node, ns=main_address_node.nsmap, ref_mapping=mainaddress_ref_mapping, target_fields=SECTION_TARGET_FIELDS["CurrentRelations"]["MainAddress"])

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
                        
            current_relations_section_mapping(root, ns)

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

            def individual_section_mapping(root, ns):
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

                    indv_general_ref_mapping = {
                        "Citizenship": REFERENCE_FIELDS["Country"],
                        "ClassificationOfIndividual": REFERENCE_FIELDS["ClassificationOfIndividual"],
                        "Education": REFERENCE_FIELDS["Education"],
                        "EmployerSector": REFERENCE_FIELDS["EconomicSector"],
                        "Employment": REFERENCE_FIELDS["Employment"],
                        "Gender": REFERENCE_FIELDS["Gender"],
                        "MaritalStatus": REFERENCE_FIELDS["MaritalStatus"],
                        "Residency": REFERENCE_FIELDS["Residency"],
                        "SocialStatus": REFERENCE_FIELDS["Employment"]
                    }

                    general_node = individual.find('b:General', namespaces=individual.nsmap)
                    if general_node is not None:
                        _remapping_response_value(node=general_node, ns=general_node.nsmap, ref_mapping=indv_general_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Individual"]["General"])

                    mainaddress_node = individual.find('b:MainAddress', namespaces=individual.nsmap)
                    if mainaddress_node is not None:
                        individual_mainaddress_ref_mapping = {
                            "City":    REFERENCE_FIELDS["City"],
                            "Country": REFERENCE_FIELDS["Country"]
                            }
                        _remapping_response_value(node=mainaddress_node, ns=mainaddress_node.nsmap, ref_mapping=individual_mainaddress_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Individual"]["MainAddress"])

                    identifications_node = individual.find('b:Identifications', namespaces=individual.nsmap)
                    if mainaddress_node is not None:
                        individual_identifications_ref_mapping = {
                            "PassportIssuerCountry" : REFERENCE_FIELDS["Country"]
                        }
                        _remapping_response_value(node=identifications_node, ns=identifications_node.nsmap, ref_mapping=individual_identifications_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Individual"]["Identifications"])  
            individual_section_mapping(root, ns)
            
            def company_section_mapping(root, ns):
                company = root.find('.//a:Company', namespaces=ns)
                if company is not None:
                    identifications_com = company.find('b:Identifications', namespaces =company.nsmap)
                    if identifications_com is not None:
                        company_scoreId = identifications_com.find('b:IdScoreId', namespaces=company.nsmap)
                        identifications_com.remove(company_scoreId)
                        identifications_com.append(company_scoreId)
                        if company_scoreId is not None:
                            company_scoreId.tag = f'{{{company.nsmap["b"]}}}PefindoId'

                    general_node = company.find('b:General', namespaces=company.nsmap)
                    if general_node is not None:
                        company_general_ref_mapping = {
                            "Category": REFERENCE_FIELDS["Category"],
                            "EconomicSector": REFERENCE_FIELDS["EconomicSector"],
                            "LegalForm": REFERENCE_FIELDS["LegalForm"],
                            "MarketListed": REFERENCE_FIELDS["MarketListed"],
                            "RatingAuthority": REFERENCE_FIELDS["RatingAuthority"],
                        }
                        _remapping_response_value(node=general_node, ns=general_node.nsmap, ref_mapping=company_general_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Company"]["General"])

                    mainaddress_node = company.find('b:MainAddress', namespaces=company.nsmap)
                    if mainaddress_node is not None:
                        company_mainaddress_ref_mapping = {
                            "City": REFERENCE_FIELDS["City"],
                            "Country": REFERENCE_FIELDS["Country"]
                        }
                        _remapping_response_value(node=mainaddress_node, ns=mainaddress_node.nsmap, ref_mapping=company_mainaddress_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Company"]["MainAddress"])
            company_section_mapping(root, ns)

            def subject_info_history_mapping(root, ns):
                subject_info_history = root.find('.//a:SubjectInfoHistory', namespaces=ns)
                if subject_info_history is not None:
                    sih_addressList = subject_info_history.find('b:AddressList', namespaces=subject_info_history.nsmap)
                    if sih_addressList is not None:
                        sih_address_ref_mapping = {
                            "Item": REFERENCE_FIELDS["Item"],
                            "Subscriber": REFERENCE_FIELDS["Subscriber"]
                        }
                        for sih_address in sih_addressList.findall('b:Address', namespaces=subject_info_history.nsmap):
                            _remapping_response_value(node=sih_address, ns=sih_address.nsmap, ref_mapping=sih_address_ref_mapping, target_fields=SECTION_TARGET_FIELDS["SubjectInfoHistory"]["Address"])
                        
                    sih_contactList = subject_info_history.find('b:ContactList', namespaces=subject_info_history.nsmap)
                    if sih_contactList is not None:
                        sih_contact_ref_mapping = {
                            "Item": REFERENCE_FIELDS["Item"],
                            "Subscriber": REFERENCE_FIELDS["Subscriber"]
                        }
                        for sih_contact in sih_contactList.findall('b:Contact', namespaces=subject_info_history.nsmap):
                            _remapping_response_value(node=sih_contact, ns=sih_contact.nsmap, ref_mapping=sih_contact_ref_mapping, target_fields=SECTION_TARGET_FIELDS["SubjectInfoHistory"]["Contact"])

                    sih_generalList = subject_info_history.find('b:GeneralList', namespaces=subject_info_history.nsmap)
                    if sih_generalList is not None:
                        sih_general_ref_mapping = {
                            "Item": REFERENCE_FIELDS["Item"],
                            "Subscriber": REFERENCE_FIELDS["Subscriber"]
                        }
                        for sih_general in sih_generalList.findall('b:General', namespaces=subject_info_history.nsmap):
                            _remapping_response_value(node=sih_general, ns=sih_general.nsmap, ref_mapping=sih_general_ref_mapping, target_fields=SECTION_TARGET_FIELDS["SubjectInfoHistory"]["General"])

                    sih_identificationsList = subject_info_history.find('b:IdentificationsList', namespaces=subject_info_history.nsmap)
                    if sih_identificationsList is not None:
                        sih_identifications_ref_mapping = {
                            "Item": REFERENCE_FIELDS["Item"],
                            "Subscriber": REFERENCE_FIELDS["Subscriber"]
                        }
                        for sih_identifications in sih_identificationsList.findall('b:Identifications', namespaces=subject_info_history.nsmap):
                            _remapping_response_value(node=sih_identifications, ns=sih_identifications.nsmap, ref_mapping=sih_identifications_ref_mapping, target_fields=SECTION_TARGET_FIELDS["SubjectInfoHistory"]["Identifications"])
            subject_info_history_mapping(root, ns)

            # Akses CIP Mengubah tag ReasonsList menjadi ReasonList
            # CIP Section Mapping
            cip = root.find('.//a:CIP', namespaces=ns)
            if cip is not None:
                record_list = cip.find('b:RecordList', namespaces=cip.nsmap)
                if record_list is not None:
                    for record in record_list.findall('b:Record', namespaces=record_list.nsmap):
                        reasons_list = record.find('b:ReasonsList', namespaces=record_list.nsmap)
                        reason_ref_mapping = {
                                "Code": REFERENCE_FIELDS["Code"],
                                "Description": REFERENCE_FIELDS["Description"],
                            }
                        for reason in reasons_list.findall('b:Reason', namespaces=cip.nsmap):
                            _remapping_response_value(node=reason, ns=reason.nsmap, ref_mapping=reason_ref_mapping, target_fields=SECTION_TARGET_FIELDS["CIP"]["Reason"])

                        if reasons_list is not None:
                            reasons_list.tag = f'{{{cip.nsmap["b"]}}}ReasonList'

            # Contracts Section Mapping
            def contracts_section_mapping(root, ns):
                contracts = root.find('.//a:Contracts', namespaces=ns)
                if contracts is not None:
                    contract_list = contracts.find('b:ContractList', namespaces=contracts.nsmap)
                    if contract_list is not None:
                        for contract in contract_list.findall('b:Contract', namespaces=contracts.nsmap):

                            # CollateralList
                            collateralList = contract.find('b:CollateralList', namespaces=contracts.nsmap)
                            if collateralList is not None:
                                collateral_ref_mapping = {
                                    "Branch": REFERENCE_FIELDS["Branch"],
                                    "CollateralStatus": REFERENCE_FIELDS["CollateralStatus"],
                                    "CollateralType": REFERENCE_FIELDS["CollateralType"],
                                    "Insurance": REFERENCE_FIELDS["Insurance"],
                                    "IsShared": REFERENCE_FIELDS["IsShared"], 
                                    "MainAddressCity": REFERENCE_FIELDS["City"], 
                                    "RatingAuthority": REFERENCE_FIELDS["RatingAuthority"], 
                                    "SecurityAssignmentType": REFERENCE_FIELDS["Description"]
                                }
                                for collateral in collateralList.findall('b:Collateral', namespaces=contracts.nsmap):
                                    _remapping_response_value(node=collateral, ns=collateral.nsmap, ref_mapping=collateral_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Contracts"]["Collateral"])

                            # RelatedSubjectsList
                            relatedSubjectsList = contract.find('b:RelatedSubjectsList', namespaces=contracts.nsmap)
                            if relatedSubjectsList is not None:
                                related_subject_ref_mapping = {
                                    "RoleOfClient": REFERENCE_FIELDS["RoleOfClient"],
                                    "SubjectType": REFERENCE_FIELDS["SubjectType"]
                                }
                                for related_subject in relatedSubjectsList.findall('b:RelatedSubject', namespaces=contracts.nsmap):
                                    _remapping_response_value(node=related_subject, ns=related_subject.nsmap, ref_mapping=related_subject_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Contracts"]["RelatedSubject"])

                            # PaymentCalendarList
                            paymentCalendarList = contract.find('b:PaymentCalendarList', namespaces=contracts.nsmap)
                            if paymentCalendarList is not None:
                                calendar_item_ref_mapping = {
                                    "DelinquencyStatus": REFERENCE_FIELDS["DelinquencyStatus"],
                                    "NegativeStatusOfContract": REFERENCE_FIELDS["NegativeStatusOfContract"],
                                }
                                for calendar_item in paymentCalendarList.findall('b:CalendarItem', namespaces=contracts.nsmap):
                                    _remapping_response_value(node=calendar_item, ns=calendar_item.nsmap, ref_mapping=calendar_item_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Contracts"]["CalendarItem"])

                            contract_ref_mapping = {
                                "Branch": REFERENCE_FIELDS["Branch"],
                                "ContractCurrency": REFERENCE_FIELDS["ContractCurrency"],
                                "ContractStatus": REFERENCE_FIELDS["ContractStatus"],
                                "ContractSubtype": REFERENCE_FIELDS["ContractSubtype"],
                                "ContractType": REFERENCE_FIELDS["ContractType"],
                                "CreditCharacteristics": REFERENCE_FIELDS["CreditCharacteristics"],
                                "CreditClassification": REFERENCE_FIELDS["CreditClassification"], 
                                "Creditor": REFERENCE_FIELDS["Creditor"],
                                "CreditorType": REFERENCE_FIELDS["Sector"],
                                "DefaultReason": REFERENCE_FIELDS["DefaultReason"],
                                "EconomicSector": REFERENCE_FIELDS["EconomicSector"],
                                "GovernmentProgram": REFERENCE_FIELDS["GovernmentProgram"],
                                "InitialInterestRateType": REFERENCE_FIELDS["InitialInterestRateType"],
                                "LastInterestRateType": REFERENCE_FIELDS["LastInterestRateType"],
                                "NegativeStatusOfContract": REFERENCE_FIELDS["NegativeStatusOfContract"],
                                "OrientationOfUse": REFERENCE_FIELDS["OrientationOfUse"],
                                "PhaseOfContract": REFERENCE_FIELDS["ContractStatus"],
                                "ProjectLocation": REFERENCE_FIELDS["City"],
                                "PurposeOfFinancing": REFERENCE_FIELDS["PurposeOfFinancing"],
                                "RestructuringReason": REFERENCE_FIELDS["RestructuringReason"],
                                "RoleOfClient": REFERENCE_FIELDS["RoleOfClient"],
                                "SyndicatedLoan": REFERENCE_FIELDS["SyndicatedLoan"],
                            }
                            _remapping_response_value(node=contract, ns=contracts.nsmap, ref_mapping=contract_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Contracts"]["Contract"])
            contracts_section_mapping(root, ns)

            # Contract Overview Section Mapping
            def contract_overview_section_mapping(root, ns):
                contract_overview = root.find('.//a:ContractOverview', namespaces=ns)
                if contract_overview is not None:
                    contract_list = contract_overview.find('b:ContractList', namespaces=contract_overview.nsmap)
                    if contract_list is not None:
                        contract_ref_mapping = {
                            "ContractStatus": REFERENCE_FIELDS["ContractStatus"],
                            "PhaseOfContract": REFERENCE_FIELDS["ContractStatusV2"],
                            "RoleOfClient": REFERENCE_FIELDS["RoleOfClient"],
                            "Sector": REFERENCE_FIELDS["Sector"],
                            "TypeOfContract": REFERENCE_FIELDS["ContractType"],
                        }
                        for contract in contract_list.findall('b:Contract', namespaces=contract_overview.nsmap):
                            _remapping_response_value(node=contract, ns=contract.nsmap, ref_mapping=contract_ref_mapping, target_fields=SECTION_TARGET_FIELDS["ContractOverview"]["Contract"])
            contract_overview_section_mapping(root, ns)

            # Contract Summary Section Mapping
            def contract_summary_section_mapping(root, ns):
                contract_summary = root.find('.//a:ContractSummary', namespaces=ns)
                if contract_summary is not None:
                    paymentCalendarList = contract_summary.find('b:PaymentCalendarList', namespaces=contract_summary.nsmap)
                    if paymentCalendarList is not None:
                        payment_calendar_ref_mapping = {
                            "NegativeStatusOfContract": REFERENCE_FIELDS["NegativeStatusOfContract"],
                        }
                        for payment_calendar in paymentCalendarList.findall('b:PaymentCalendar', namespaces=contract_summary.nsmap):
                            _remapping_response_value(node=payment_calendar, ns=payment_calendar.nsmap, ref_mapping=payment_calendar_ref_mapping, target_fields=SECTION_TARGET_FIELDS["ContractSummary"]["PaymentCalendar"])
            contract_summary_section_mapping(root, ns)

            # CIQ Section Mapping
            def ciq_section_mapping(root, ns):
                ciq = root.find('.//a:CIQ', namespaces=ns)
                if ciq is not None:
                    pass

            # Securities Section Mapping
            def securities_section_mapping(root, ns):
                securities = root.find('.//a:Securities', namespaces=ns)
                if securities is not None:
                    security_list = securities.find('b:SecurityList', namespaces=securities.nsmap)
                    if security_list is not None:
                        security_ref_mapping = {
                            "Branch": REFERENCE_FIELDS["Branch"],
                            "ContractStatus": REFERENCE_FIELDS["ContractStatus"],
                            "Creditor": REFERENCE_FIELDS["Creditor"],
                            "CurrencyOfContract": REFERENCE_FIELDS["ContractCurrency"],
                            "DefaultReason": REFERENCE_FIELDS["DefaultReason"],
                            "MarketListed": REFERENCE_FIELDS["MarketListed"],
                            "NegativeStatus": REFERENCE_FIELDS["NegativeStatusOfContract"],
                            "PurposeOfOwnership": REFERENCE_FIELDS["PurposeOfFinancing"],
                            "SecurityType": REFERENCE_FIELDS["SecurityType"],
                            "TypeofInterestRate": REFERENCE_FIELDS["TypeofInterestRate"],
                        }
                        for security in security_list.findall('b:', namespaces=securities.nsmap):
                            _remapping_response_value(node=security, ns=security.nsmap, ref_mapping=security_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Securities"]["Security"])
            securities_section_mapping(root, ns)

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
            # Disputes Section Mapping
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

            # Inquiries Section Mapping
            def inquiries_section_mapping(root, ns):
                inquiries = root.find('.//a:Inquiries', namespaces=ns)
                if inquiries is not None:
                    inquiry_list = inquiries.find('b:InquiryList', namespaces=inquiries.nsmap)
                    if inquiry_list is not None:
                        inquiry_ref_mapping = {
                            "Sector": REFERENCE_FIELDS["Sector"],
                            "SubscriberInfo": REFERENCE_FIELDS["Creditor"],
                        }
                        for inquiry in inquiry_list.findall('b:Inquiry', namespaces=inquiries.nsmap):
                            _remapping_response_value(node=inquiry, ns=inquiry.nsmap, ref_mapping=inquiry_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Inquiries"]["Inquiry"])
            inquiries_section_mapping(root, ns)

            # ReportInfo Version Update
            reportInfo = root.find('.//a:ReportInfo', namespaces=ns)
            if reportInfo is not None:
                report_version = reportInfo.find('b:Version', namespaces=reportInfo.nsmap)
                report_version.text = "553"

            xml_bytes_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_bytes_result.replace(b"v5.109", b"v5.53")
        except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            return "ERROR"

    @staticmethod
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
                        reference_code.text = generate_reference_code()
                        parent.insert(parent.index(inquiry_reason) + 1, reference_code)
                xml_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_result.replace(b"v5.53", b"v5.109").decode('utf-8')
        except Exception as e:
                logger.error(f"Error parsing XML: {e}")
                return "ERROR"