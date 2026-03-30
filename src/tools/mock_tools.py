from typing import Any

MOCK_FORECAST = {
    "product_id":  "SKU-0001",
    "horizon":     28,
    "avg_demand":  158,
    "total_28d":   4438,
    "forecast":    [158] * 28,
    "lower":       [140] * 28,
    "upper":       [176] * 28,
    "dates":       [f"2026-04-{i:02d}" for i in range(1, 29)]
}

MOCK_RISK_ALERTS = [
    {"supplier_id": "SUP-0038", "supplier_name": "Knorr-Bremse AG — Werk 38",
     "risk_score": 0.532, "predicted_risk": "High"},
    {"supplier_id": "SUP-0057", "supplier_name": "Webasto Group — Werk 57",
     "risk_score": 0.585, "predicted_risk": "High"},
    {"supplier_id": "SUP-0100", "supplier_name": "Bosch Automotive GmbH — Werk 100",
     "risk_score": 0.625, "predicted_risk": "High"},
]

MOCK_SUPPLIER_RISK = {
    "supplier_id":   "SUP-0038",
    "supplier_name": "Knorr-Bremse AG — Werk 38",
    "risk_level":    "High",
    "confidence":    0.91,
    "raw_score":     0.532,
    "alert":         True,
    "top_features": [
        {"feature": "geo_risk_score",       "shap_value": 1.42},
        {"feature": "single_source",        "shap_value": 0.98},
        {"feature": "lead_time_variance",   "shap_value": 0.87},
        {"feature": "financial_risk_score", "shap_value": 0.63},
        {"feature": "num_alternatives",     "shap_value": -0.41},
    ]
}

MOCK_ERP_RESPONSE = {
    "question": "What is the current stock and reorder status for SKU-0001?",
    "answer":   (
        "Current stock for SKU-0001 (Brake Caliper Assembly) is 1,200 units. "
        "The safety stock threshold is 500 units and the reorder point is 800 units. "
        "At the forecasted consumption rate of 158 units per day, current stock "
        "covers approximately 7.6 days. An open purchase order PO-000042 for "
        "2,000 units is expected from Knorr-Bremse AG with delivery in 14 days."
    ),
    "sources": [
        {"record_id": "SKU-0001", "table": "stock_levels",   "relevance": 0.91},
        {"record_id": "PO-000042", "table": "purchase_orders", "relevance": 0.84},
    ]
}


def mock_get_forecast(product_id: str) -> dict:
    result = MOCK_FORECAST.copy()
    result["product_id"] = product_id
    return result


def mock_get_risk_alerts() -> list:
    return MOCK_RISK_ALERTS


def mock_get_supplier_risk(supplier_id: str) -> dict:
    result = MOCK_SUPPLIER_RISK.copy()
    result["supplier_id"] = supplier_id
    return result


def mock_erp_query(question: str) -> dict:
    result = MOCK_ERP_RESPONSE.copy()
    result["question"] = question
    return result