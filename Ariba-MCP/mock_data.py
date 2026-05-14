"""
Mock data for SAP Ariba Event Management API.

Used when ARIBA_USE_MOCK=true or when no credentials are configured.
Mirrors (a subset of) the response shape from:
https://help.sap.com/docs/ariba-apis/event-management-api/event-management-api-v2-endpoints
"""

from datetime import datetime, timedelta, timezone

_now = datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


EVENTS = [
    {
        "eventId": "Doc1234567890",
        "title": "RFP - Matérias-primas químicas 2026",
        "type": "RFP",
        "status": "Closed",
        "ownerName": "Carla Mendes",
        "currency": "BRL",
        "startDate": _iso(_now - timedelta(days=20)),
        "endDate": _iso(_now - timedelta(days=5)),
        "description": "Cotação anual de matérias-primas químicas para a planta de Campinas.",
        "suppliersInvited": 6,
        "suppliersParticipated": 4,
        "suppliersDeclined": 2,
    },
    {
        "eventId": "Doc2233445566",
        "title": "Leilão Reverso - Logística rodoviária Sudeste",
        "type": "Auction",
        "status": "Open",
        "ownerName": "Bruno Lima",
        "currency": "BRL",
        "startDate": _iso(_now - timedelta(days=1)),
        "endDate": _iso(_now + timedelta(days=3)),
        "description": "Leilão reverso para contratação de frete dedicado SP-RJ-MG.",
        "suppliersInvited": 8,
        "suppliersParticipated": 5,
        "suppliersDeclined": 1,
    },
    {
        "eventId": "Doc9988776655",
        "title": "RFI - Soluções de embalagem sustentável",
        "type": "RFI",
        "status": "Closed",
        "ownerName": "Patrícia Souza",
        "currency": "USD",
        "startDate": _iso(_now - timedelta(days=60)),
        "endDate": _iso(_now - timedelta(days=45)),
        "description": "Levantamento de mercado para embalagens biodegradáveis.",
        "suppliersInvited": 10,
        "suppliersParticipated": 7,
        "suppliersDeclined": 3,
    },
]


PARTICIPANTS = {
    "Doc1234567890": [
        {"supplierId": "S-001", "supplierName": "Química Brasil Ltda", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "S-002", "supplierName": "PoliChem S.A.", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "S-003", "supplierName": "Sigma Insumos", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "S-004", "supplierName": "AlfaQuímica", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "S-005", "supplierName": "BetaChem", "status": "Declined", "contact": "[email protected]"},
        {"supplierId": "S-006", "supplierName": "Gama Ind. Química", "status": "Declined", "contact": "[email protected]"},
    ],
    "Doc2233445566": [
        {"supplierId": "L-101", "supplierName": "TransLog Sudeste", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "L-102", "supplierName": "RodoBrasil", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "L-103", "supplierName": "ExpressCargo", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "L-104", "supplierName": "Via Rápida Log.", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "L-105", "supplierName": "MegaFrete", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "L-106", "supplierName": "Pequena Transp.", "status": "Declined", "contact": "[email protected]"},
        {"supplierId": "L-107", "supplierName": "Não Respondeu Log.", "status": "NoResponse", "contact": "[email protected]"},
        {"supplierId": "L-108", "supplierName": "Sem Capacidade Log.", "status": "NoResponse", "contact": "[email protected]"},
    ],
    "Doc9988776655": [
        {"supplierId": "P-201", "supplierName": "EcoPack", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "P-202", "supplierName": "GreenWrap", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "P-203", "supplierName": "BioBox", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "P-204", "supplierName": "PaperPlus", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "P-205", "supplierName": "SustainPack", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "P-206", "supplierName": "ZeroPlastic", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "P-207", "supplierName": "ReUseCo", "status": "Participated", "contact": "[email protected]"},
        {"supplierId": "P-208", "supplierName": "OldStylePack", "status": "Declined", "contact": "[email protected]"},
        {"supplierId": "P-209", "supplierName": "Tradicional Emb.", "status": "Declined", "contact": "[email protected]"},
        {"supplierId": "P-210", "supplierName": "NãoSustentável SA", "status": "Declined", "contact": "[email protected]"},
    ],
}


BIDS = {
    "Doc1234567890": [
        {"supplierId": "S-001", "supplierName": "Química Brasil Ltda", "lineItem": "Soda Cáustica 50%", "amount": 4.85, "currency": "BRL", "unit": "kg", "submittedAt": _iso(_now - timedelta(days=7))},
        {"supplierId": "S-002", "supplierName": "PoliChem S.A.", "lineItem": "Soda Cáustica 50%", "amount": 4.72, "currency": "BRL", "unit": "kg", "submittedAt": _iso(_now - timedelta(days=7))},
        {"supplierId": "S-003", "supplierName": "Sigma Insumos", "lineItem": "Soda Cáustica 50%", "amount": 4.95, "currency": "BRL", "unit": "kg", "submittedAt": _iso(_now - timedelta(days=6))},
        {"supplierId": "S-004", "supplierName": "AlfaQuímica", "lineItem": "Soda Cáustica 50%", "amount": 4.68, "currency": "BRL", "unit": "kg", "submittedAt": _iso(_now - timedelta(days=6))},
        {"supplierId": "S-001", "supplierName": "Química Brasil Ltda", "lineItem": "Ácido Sulfúrico 98%", "amount": 2.10, "currency": "BRL", "unit": "kg", "submittedAt": _iso(_now - timedelta(days=7))},
        {"supplierId": "S-002", "supplierName": "PoliChem S.A.", "lineItem": "Ácido Sulfúrico 98%", "amount": 2.05, "currency": "BRL", "unit": "kg", "submittedAt": _iso(_now - timedelta(days=7))},
        {"supplierId": "S-004", "supplierName": "AlfaQuímica", "lineItem": "Ácido Sulfúrico 98%", "amount": 1.99, "currency": "BRL", "unit": "kg", "submittedAt": _iso(_now - timedelta(days=6))},
    ],
    "Doc2233445566": [
        {"supplierId": "L-101", "supplierName": "TransLog Sudeste", "lineItem": "Frete SP-RJ (carga fechada)", "amount": 3200.00, "currency": "BRL", "unit": "viagem", "submittedAt": _iso(_now - timedelta(hours=20))},
        {"supplierId": "L-102", "supplierName": "RodoBrasil", "lineItem": "Frete SP-RJ (carga fechada)", "amount": 3150.00, "currency": "BRL", "unit": "viagem", "submittedAt": _iso(_now - timedelta(hours=18))},
        {"supplierId": "L-103", "supplierName": "ExpressCargo", "lineItem": "Frete SP-RJ (carga fechada)", "amount": 3080.00, "currency": "BRL", "unit": "viagem", "submittedAt": _iso(_now - timedelta(hours=12))},
        {"supplierId": "L-104", "supplierName": "Via Rápida Log.", "lineItem": "Frete SP-RJ (carga fechada)", "amount": 2990.00, "currency": "BRL", "unit": "viagem", "submittedAt": _iso(_now - timedelta(hours=8))},
        {"supplierId": "L-105", "supplierName": "MegaFrete", "lineItem": "Frete SP-RJ (carga fechada)", "amount": 2950.00, "currency": "BRL", "unit": "viagem", "submittedAt": _iso(_now - timedelta(hours=2))},
    ],
    "Doc9988776655": [],  # RFI sem lances financeiros
}
