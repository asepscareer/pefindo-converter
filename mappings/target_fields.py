SECTION_TARGET_FIELDS = {
    "CIP": {
        "Reason": ["Code", "Description"]
    },
    "Company": {
        "General": ["Category", "EconomicSector", "LegalForm", "MarketListed", "RatingAuthority"],
        "MainAddress": ["City", "Country"]
    },
    "ContractOverview": {
        "Contract": ["ContractStatus", "PhaseOfContract", "RoleOfClient", "Sector", "TypeOfContract"]
    },
    "ContractSummary": {
        "PaymentCalendar": ["NegativeStatusOfContract"]
    },
    "Contracts": {
        "CalendarItem": ["DelinquencyStatus", "NegativeStatusOfContract"],
        "Collateral": [
            "Branch", "CollateralStatus", "CollateralType", "Insurance",
            "IsShared", "MainAddressCity", "RatingAuthority", "SecurityAssignmentType"
        ],
        "Contract": [
            "Branch", "ContractCurrency", "ContractStatus", "ContractSubtype",
            "ContractType", "CreditCharacteristics", "CreditClassification", 
            "Creditor", "CreditorType", "DefaultReason", "EconomicSector", 
            "GovernmentProgram", "InitialInterestRateType", "LastInterestRateType", 
            "NegativeStatusOfContract", "OrientationOfUse", "PhaseOfContract", 
            "ProjectLocation", "PurposeOfFinancing", "RestructuringReason", 
            "RoleOfClient", "SyndicatedLoan"
        ],
        "RelatedSubject": ["RoleOfClient", "SubjectType"]
    },
    "CurrentRelations": {
        "MainAddress": ["City", "Country"],
        "RelatedParty": ["Gender", "IDNumberType", "SubjectStatus", "SubjectType", "TypeOfRelation"]
    },
    "Individual": {
        "General": [
            "Citizenship", "ClassificationOfIndividual", "Education", 
            "EmployerSector", "Employment", "Gender", "MaritalStatus", 
            "Residency", "SocialStatus"
        ],
        "Identifications": ["PassportIssuerCountry"],
        "MainAddress": ["City", "Country"]
    },
    "Inquiries": {
        "Inquiry": ["Sector", "SubscriberInfo"]
    },
    "Securities": {
        "Security": [
            "Branch", "ContractStatus", "Creditor", "CurrencyOfContract", 
            "DefaultReason", "MarketListed", "MarketValue", "NegativeStatus", 
            "PurposeOfOwnership", "SecurityType", "TypeofInterestRate"
        ]
    },
    "SubjectInfoHistory": {
        "Address": ["Item", "Subscriber"],
        "Contact": ["Item", "Subscriber"],
        "General": ["Item", "Subscriber"],
        "Identifications": ["Item", "Subscriber"]
    }
}