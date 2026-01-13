import logging
from lxml import etree as ET

from utils import generate_reference_code
from mappings.city import CITY_MAPPING
from mappings.country_codes import COUNTRY_CODES_MAPPING
from mappings.target.target_fields import SECTION_TARGET_FIELDS

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

                                related_party_ref_mapping = {
                                    "Gender": {"Male":"Laki-laki","Female":"Perempuan"},
                                    "IDNumberType": {"IdCard":"KTP","Passport":"Paspor","DriverLicense":"SIM"},
                                    "SubjectStatus": {"Active":"Aktif","Inactive":"Tidak Aktif"},
                                }
                                related_party_target_fields = ["Gender","IDNumberType","SubjectStatus","SubjectType","TypeOfRelation"]
                                _remapping_response_value(node=related_party, ns=current_relations.nsmap, ref_mapping=related_party_ref_mapping, target_fields=related_party_target_fields)

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
                        "Citizenship": {"ID": "Indonesia", "US": "United States"},
                        "Gender": {"Male": "Laki-laki", "Female": "Perempuan"},
                        "MaritalStatus": {"Married": "Menikah", "Single": "Belum Menikah"},
                        "Education": {"NoEducation": "Tidak Berpendidikan", "01": "SD", "02": "SMP", "03": "SMA"},
                    }

                    indv_general_target_fields = [
                            'Citizenship', 'ClassificationOfIndividual', 'Education', 
                            'EmployerSector', 'Employment', 'Gender', 'MaritalStatus', 
                            'Residency', 'SocialStatus'
                        ]

                    general_node = individual.find('b:General', namespaces=individual.nsmap)
                    if general_node is not None:
                        _remapping_response_value(node=general_node, ns=individual.nsmap, ref_mapping=indv_general_ref_mapping, target_fields=indv_general_target_fields)

                    individual_mainaddress_ref_mapping = {
                        "City":    CITY_MAPPING,
                        "Country": COUNTRY_CODES_MAPPING
                    }

                    mainaddress_node = individual.find('b:MainAddress', namespaces=individual.nsmap)
                    if mainaddress_node is not None:
                        _remapping_response_value(node=mainaddress_node, ns=individual.nsmap, ref_mapping=individual_mainaddress_ref_mapping, target_fields=SECTION_TARGET_FIELDS["Individual"]["MainAddress"])
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

                    company_general_ref_mapping = {
                        "Category": {"01": "Perusahaan", "02": "Perusahaan", "03": "Perusahaan"},
                        "EconomicSector": {"01": "Industri", "02": "Perdagangan", "03": "Jasa"},
                        "LegalForm": {"01": "Perseroan Terbatas", "02": "Koperasi", "03": "Perorangan"},
                        "MarketListed": {"Yes": "Ya", "No": "Tidak"},
                        "RatingAuthority": {"Pefindo": "Pefindo", "Other": "Lainnya"},
                    }

                    company_general_target_fields = [
                        'Category', 'EconomicSector', 'LegalForm', 'MarketListed', 'RatingAuthority'
                    ]

                    general_node = company.find('b:General', namespaces=company.nsmap)
                    if general_node is not None:
                        _remapping_response_value(node=general_node, ns=company.nsmap, ref_mapping=company_general_ref_mapping, target_fields=company_general_target_fields)

                    company_mainaddress_ref_mapping = {
                        "City":     {"Jakarta": "DKI Jakarta", "Other": "Lainnya", "Bandung": "Jawa Barat"},
                        "Country":  {"ID": "Indonesia"}
                    }

                    company_mainaddress_target_fields = ['City', 'Country']

                    mainaddress_node = company.find('b:MainAddress', namespaces=company.nsmap)
                    if mainaddress_node is not None:
                        _remapping_response_value(node=mainaddress_node, ns=company.nsmap, ref_mapping=company_mainaddress_ref_mapping, target_fields=company_mainaddress_target_fields)
            company_section_mapping(root, ns)

            def subject_info_history_mapping(root, ns):
                subject_info_history = root.find('.//a:SubjectInfoHistory', namespaces=ns)
                if subject_info_history is not None:
                    sih_addressList = subject_info_history.find('b:AddressList', namespaces=subject_info_history.nsmap)
                    if sih_addressList is not None:
                        for sih_address in sih_addressList.findall('b:Address', namespaces=subject_info_history.nsmap):
                            sih_address_ref_mapping = {
                                "Item": {"MainAddress": "Alamat Utama", "OtherAddress": "Alamat Lainnya"},
                            }
                            sih_address_target_fields = ['Item', 'Subscriber', 'ValidFrom', 'ValidTo', 'Value']
                            _remapping_response_value(node=sih_address, ns=sih_addressList.nsmap, ref_mapping=sih_address_ref_mapping, target_fields=sih_address_target_fields)
                        
                    sih_contactList = subject_info_history.find('b:ContactList', namespaces=subject_info_history.nsmap)
                    if sih_contactList is not None:
                        for sih_contact in sih_contactList.findall('b:Contact', namespaces=subject_info_history.nsmap):
                            sih_contact_ref_mapping = {
                                "Item": {"Email": "Surel", "FixedLine": "Surel"},
                            }
                            sih_contact_target_fields = ['Item', 'Subscriber', 'ValidFrom', 'ValidTo', 'Value']
                            _remapping_response_value(node=sih_contact, ns=sih_contactList.nsmap, ref_mapping=sih_contact_ref_mapping, target_fields=sih_contact_target_fields)

                    sih_generalList = subject_info_history.find('b:GeneralList', namespaces=subject_info_history.nsmap)
                    if sih_generalList is not None:
                        for sih_general in sih_generalList.findall('b:General', namespaces=subject_info_history.nsmap):
                            sih_general_ref_mapping = {
                                "Item": {"DebtorName": "Nama", "DateOfBirth": "Tanggal Lahir", "MothersMaidenName": "Nama Ibu Kandung"},
                            }
                            sih_general_target_fields = ['Item', 'Subscriber', 'ValidFrom', 'ValidTo', 'Value']
                            _remapping_response_value(node=sih_general, ns=sih_generalList.nsmap, ref_mapping=sih_general_ref_mapping, target_fields=sih_general_target_fields)

                    sih_identificationsList = subject_info_history.find('b:IdentificationsList', namespaces=subject_info_history.nsmap)
                    if sih_identificationsList is not None:
                        for sih_identifications in sih_identificationsList.findall('b:Identifications', namespaces=subject_info_history.nsmap):
                            sih_identifications_ref_mapping = {
                                "Item": {"IdNumber": "KTP", "TaxNumber": "No. Pajak"},
                            }
                            sih_identifications_target_fields = ['Item', 'Subscriber', 'ValidFrom', 'ValidTo', 'Value']
                            _remapping_response_value(node=sih_identifications, ns=sih_identificationsList.nsmap, ref_mapping=sih_identifications_ref_mapping, target_fields=sih_identifications_target_fields)
            subject_info_history_mapping(root, ns)

            # Akses CIP Mengubah tag ReasonsList menjadi ReasonList
            # CIP Section Mapping
            cip = root.find('.//a:CIP', namespaces=ns)
            if cip is not None:
                record_list = cip.find('b:RecordList', namespaces=cip.nsmap)
                if record_list is not None:
                    for record in record_list.findall('b:Record', namespaces=cip.nsmap):
                        record_ref_mapping = {
                            "Grade": {"A3": "Sangat Baik", "Others": "Lainnya"},
                            "ProbabilityOfDefault": {"4.34": "Sangat Baik", "Others": "Lainnya"},
                        }
                        record_target_fields = ['Date', 'Grade', 'ProbabilityOfDefault', 'Score', 'Trend']

                        _remapping_response_value(node=record, ns=cip.nsmap, ref_mapping=record_ref_mapping, target_fields=record_target_fields)

                        reasons_list = record.find('b:ReasonsList', namespaces=cip.nsmap)
                        if reasons_list is not None:
                            reasons_list.tag = f'{{{cip.nsmap["b"]}}}ReasonList'

                            for reason in reasons_list.findall('b:Reason', namespaces=cip.nsmap):
                                reason_ref_mapping = {
                                    "Code": {"NQS1": "Asep Saputra", "02": "Lainnya"},
                                    "Description": {"Dummy scoring": "Ini Hanya Dummy scoring", "Others": "Lainnya"},
                                }

                                reason_target_fields = ['Code', 'Description']
                                _remapping_response_value(node=reason, ns=cip.nsmap, ref_mapping=reason_ref_mapping, target_fields=reason_target_fields)

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
                                for collateral in collateralList.findall('b:Collateral', namespaces=contracts.nsmap):
                                    collateral_ref_mapping = {
                                        "AppraisalValue": {"1000000000": "1500000000"},
                                    }
                                    collateral_target_fields = ["AppraisalValue","BankValuationDate","BankValue","Branch","CollateralAcceptanceDate","CollateralAppraisalAuthority","CollateralCode","CollateralDescription","CollateralOwnerName",
                                                                "CollateralRating","CollateralStatus","CollateralType","CollateralValue","HasMultipleCollaterals","Insurance","IsShared","MainAddressAddressLine","MainAddressCity",
                                                                "MainAddressStreet","ProofOfOwnership","RatingAuthority","SecurityAssignmentType","SharedPortion","ValuationDate"]
                                    _remapping_response_value(node=collateral, ns=contracts.nsmap, ref_mapping=collateral_ref_mapping, target_fields=collateral_target_fields)

                            # RelatedSubjectsList
                            relatedSubjectsList = contract.find('b:RelatedSubjectsList', namespaces=contracts.nsmap)
                            if relatedSubjectsList is not None:
                                for related_subject in relatedSubjectsList.findall('b:RelatedSubject', namespaces=contracts.nsmap):
                                    related_subject_ref_mapping = {
                                        "TaxNumber": {"0": "1", "Other": "Lainnya"},
                                    }
                                    related_subject_target_fields = ["ExpectedEndDate","GuarancyDescription","GuaranteeAmount","JointAccountSequence","Name","NationalID","PassportNumber","RealEndDate",
                                                                     "RegistrationNumber","RelationshipType","RoleOfClient","StartDate","SubjectType","TaxNumber"]
                                    _remapping_response_value(node=related_subject, ns=contracts.nsmap, ref_mapping=related_subject_ref_mapping, target_fields=related_subject_target_fields)

                            # PaymentCalendarList
                            paymentCalendarList = contract.find('b:PaymentCalendarList', namespaces=contracts.nsmap)
                            if paymentCalendarList is not None:
                                for calendar_item in paymentCalendarList.findall('b:CalendarItem', namespaces=contracts.nsmap):
                                    calendar_item_ref_mapping = {
                                        "DelinquencyStatus": {"Current": "Lancar", "Others": "Lainnya"},
                                        "NegativeStatusOfContract": {"NoNegativeStatus": "Tidak ada status negatif", "Others": "Lainnya"},
                                    }
                                    calendar_item_target_fields = ["Date","DelinquencyStatus","InterestRate","NegativeStatusOfContract","OutstandingAmount","PastDueAmount","PastDueDays"]
                                    _remapping_response_value(node=calendar_item, ns=contracts.nsmap, ref_mapping=calendar_item_ref_mapping, target_fields=calendar_item_target_fields)

                            """
                            Filed Ini dilakukan nanti
                            Disputes, InitialTotalAmount, OutstandingAmount, PastDueAmount, PastDueInterest,
                            Penalty, PrincipalArrears, PrincipalBalance, ProjectValue,
                            TotalAmount, TotalFacilityAmount, TotalTakenAmount
                            """

                            contract_ref_mapping = {
                                "Creditor": {"PT Woka Internasional": "Hana Bank"},
                                "CreditorType": {"Multifinance": "Bank"},
                                "NegativeStatusOfContract": {"NoNegativeStatus": "Tidak ada status negatif", "Others": "Lainnya"}
                            }

                            contract_target_fields = [
                                "BankBeneficiary","Branch", "ConditionDate", "ContractCode","ContractCurrency","ContractStatus",
                                "ContractSubtype","ContractType", "CreditCharacteristics","CreditClassification","CreditUsageInLast30Days","Creditor","CreditorType","DefaultDate","DefaultReason","DefaultReasonDescription",
                                "DelinquencyDate","Description","DisbursementDate","EconomicSector","GovernmentProgram","GuarantyDeposit","InitialAgreementDate", "InitialAgreementNumber",
                                "InitialInterestRate","InitialInterestRateType","InitialRestructuringDate","InitialTotalAmount","InterestArrears","InterestArrearsFrequency","LastAgreementDate","LastAgreementNumber",
                                "LastDelinquency90PlusDays","LastInterestRate","LastInterestRateType","LastUpdate","MaturityDate","NameOfInsured","NegativeStatusOfContract","OrientationOfUse",
                                "PastDueDays","PhaseOfContract","PrincipalArrearsFrequency","ProjectLocation", "ProlongationCounter","PurposeOfFinancing","RealEndDate","RestructuredCount",
                                "RestructuringDate","RestructuringReason","RoleOfClient","StartDate","SyndicatedLoan", "WorstPastDueAmount","WorstPastDueDays"
                            ]
                            _remapping_response_value(node=contract, ns=contracts.nsmap, ref_mapping=contract_ref_mapping, target_fields=contract_target_fields)
            contracts_section_mapping(root, ns)

            # Contract Overview Section Mapping
            def contract_overview_section_mapping(root, ns):
                contract_overview = root.find('.//a:ContractOverview', namespaces=ns)
                if contract_overview is not None:
                    contract_list = contract_overview.find('b:ContractList', namespaces=contract_overview.nsmap)
                    if contract_list is not None:
                        for contract in contract_list.findall('b:Contract', namespaces=contract_overview.nsmap):
                            contract_ref_mapping = {
                                "ContractStatus": {"Settled": "Berhasil"},
                                "Sector": {"Multifinance": "Bank"},
                            }

                            contract_target_fields = [ "ContractStatus", "OutstandingAmount", "PastDueAmount", "PastDueDays",
                                                      "PhaseOfContract", "RoleOfClient", "Sector", "StartDate", "TotalAmount", "TypeOfContract"
                            ]
                            _remapping_response_value(node=contract, ns=contract_overview.nsmap, ref_mapping=contract_ref_mapping, target_fields=contract_target_fields)
            contract_overview_section_mapping(root, ns)

            # Contract Summary Section Mapping
            def contract_summary_section_mapping(root, ns):
                contract_summary = root.find('.//a:ContractSummary', namespaces=ns)
                if contract_summary is not None:
                    paymentCalendarList = contract_summary.find('b:PaymentCalendarList', namespaces=contract_summary.nsmap)
                    if paymentCalendarList is not None:
                        for payment_calendar in paymentCalendarList.findall('b:PaymentCalendar', namespaces=contract_summary.nsmap):
                            payment_calendar_ref_mapping = {
                                "NegativeStatusOfContract": {"NoNegativeStatus": "Tidak ada status negatif", "Others": "Lainnya"},
                            }
                            payment_calendar_target_fields = ["ContractsSubmitted", "Date", "NegativeStatusOfContract", "OutstandingAmount", "PastDueAmount", "PastDueDays"]
                            _remapping_response_value(node=payment_calendar, ns=contract_summary.nsmap, ref_mapping=payment_calendar_ref_mapping, target_fields=payment_calendar_target_fields)
            contract_summary_section_mapping(root, ns)

            # CIQ Section Mapping
            def ciq_section_mapping(root, ns):
                ciq = root.find('.//a:CIQ', namespaces=ns)
                if ciq is not None:
                    pass
                    # CIQ.Detail.NumberOfCancelledClosedContracts
                    # CIQ.Detail.NumberOfCancelledClosedContracts
                    # CIQ.Detail.NumberOfSubscribersMadeInquiriesLast14Days
                    # CIQ.Detail.NumberOfSubscribersMadeInquiriesLast2Days
                    # CIQ.Summary.DateOfLastFraudRegistrationPrimarySubject
                    # CIQ.Summary.DateOfLastFraudRegistrationThirdParty
                    # CIQ.Summary.NumberOfFraudAlertsPrimarySubject
                    # CIQ.Summary.NumberOfFraudAlertsThirdParty
            ciq_section_mapping(root, ns)


            # Securities Section Mapping
            def securities_section_mapping(root, ns):
                securities = root.find('.//a:Securities', namespaces=ns)
                if securities is not None:
                    security_list = securities.find('b:SecurityList', namespaces=securities.nsmap)
                    if security_list is not None:
                        for security in security_list.findall('b:Security', namespaces=securities.nsmap):
                            security_ref_mapping = {
                                "ContractStatus": {"Settled": "Berhasil"},
                                "SecurityType": {"LandAndBuilding": "Tanah dan Bangunan", "Vehicle": "Kendaraan", "Other": "Lainnya"},
                            }
                            security_target_fields = ["AcquisitionAmount","AcquisitionDate","Branch","ConditionDate","ContractCode",
                                                      "ContractStatus","Creditor","CurrencyOfContract","DefaultDate","DefaultReason","DefaultReasonDescription",
                                                    "DelinquencyDate","Description","InitialTotalAmount","InterestRate","IssueDate","IssuerName","LastUpdate",
                                                    "MarketListed","MarketValue","MaturityDate","NegativeStatus", "OutstandingAmount","PastDueDays","PreviousContractCode",
                                                    "PrincipalArrears","PurposeOfOwnership","Rating","RealEndDate","SecurityType","SovereignRate","TypeofInterestRate"]
                            _remapping_response_value(node=security, ns=securities.nsmap, ref_mapping=security_ref_mapping, target_fields=security_target_fields)
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
                # Inquiries.Summary.NumberOfInquiriesLast12Months
                # Inquiries.Summary.NumberOfInquiriesLast1Month
                # Inquiries.Summary.NumberOfInquiriesLast24Months
                # Inquiries.Summary.NumberOfInquiriesLast3Months
                # Inquiries.Summary.NumberOfInquiriesLast6Months
                # Inquiries.InquiryList.Inquiry.DateOfInquiry
                # Inquiries.InquiryList.Inquiry.Product
                # Inquiries.InquiryList.Inquiry.Reason
                # Inquiries.InquiryList.Inquiry.Sector
                # Inquiries.InquiryList.Inquiry.SubscriberInfo
                inquiries = root.find('.//a:Inquiries', namespaces=ns)
                if inquiries is not None:
                    inquiry_list = inquiries.find('b:InquiryList', namespaces=inquiries.nsmap)
                    if inquiry_list is not None:
                        for inquiry in inquiry_list.findall('b:Inquiry', namespaces=inquiries.nsmap):
                            inquiry_ref_mapping = {
                                "Sector": {"NotSpecified": "Bank", "Others": "Liannya"},
                                "SubscriberInfo": {"PT Creditinfo Indonesia": "Hana Bank", "Others": "Lainnya"},
                            }

                            inquiry_target_fields = ["DateOfInquiry", "Product", "Reason", "Sector", "SubscriberInfo", "InquiryType"]
                            _remapping_response_value(node=inquiry, ns=inquiries.nsmap, ref_mapping=inquiry_ref_mapping, target_fields=inquiry_target_fields)
            inquiries_section_mapping(root, ns)

            # ReportInfo Version Update
            reportInfo = root.find('.//a:ReportInfo', namespaces=ns)
            if reportInfo is not None:
                report_version = reportInfo.find('b:Version', namespaces=reportInfo.nsmap)
                report_version.text = "553"

            xml_bytes_result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            return xml_bytes_result.replace(b"v5.109", b"v5.53")
        except Exception as e:
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