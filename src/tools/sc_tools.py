import os
import requests
from dotenv import load_dotenv
from src.tools.mock_tools import mock_get_forecast, mock_get_risk_alerts

load_dotenv()

SC_API_URL    = os.getenv("SC_API_URL", "http://localhost:8002")
USE_MOCK      = os.getenv("USE_MOCK_TOOLS", "true").lower() == "true"


def get_demand_forecast(product_id: str) -> dict:
    if USE_MOCK:
        return mock_get_forecast(product_id)
    try:
        resp = requests.post(
            f"{SC_API_URL}/forecast",
            json    = {"product_id": product_id},
            timeout = 30
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e), "product_id": product_id}


def get_risk_alerts() -> list:
    if USE_MOCK:
        return mock_get_risk_alerts()
    try:
        resp = requests.get(f"{SC_API_URL}/risk/alerts", timeout=15)
        return resp.json()
    except Exception as e:
        return [{"error": str(e)}]


def format_forecast_summary(forecast: dict) -> str:
    if "error" in forecast:
        return f"Forecast unavailable: {forecast['error']}"
    return (
        f"Product {forecast['product_id']}: "
        f"avg demand {forecast['avg_demand']} units/day, "
        f"total 28-day demand {forecast['total_28d']} units."
    )


def format_risk_summary(alerts: list) -> str:
    if not alerts or "error" in alerts[0]:
        return "No risk alert data available."
    lines = [
        f"  - {a['supplier_id']} ({a['supplier_name']}): score {a['risk_score']:.3f}"
        for a in alerts[:5]
    ]
    return f"{len(alerts)} high-risk suppliers:\n" + "\n".join(lines)