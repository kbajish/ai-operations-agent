import os
import requests
from dotenv import load_dotenv
from src.tools.mock_tools import mock_erp_query

load_dotenv()

ERP_API_URL = os.getenv("ERP_API_URL", "http://localhost:8001")
USE_MOCK    = os.getenv("USE_MOCK_TOOLS", "true").lower() == "true"


def query_erp(question: str) -> dict:
    if USE_MOCK:
        return mock_erp_query(question)
    try:
        resp = requests.post(
            f"{ERP_API_URL}/query",
            json    = {"question": question},
            timeout = 60
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e), "answer": "ERP system unavailable."}


def format_erp_answer(result: dict) -> str:
    if "error" in result:
        return f"ERP query failed: {result['error']}"
    return result.get("answer", "No answer returned.")