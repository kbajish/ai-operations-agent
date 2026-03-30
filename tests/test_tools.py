import os
os.environ["USE_MOCK_TOOLS"] = "true"


def test_mock_forecast_returns_correct_structure():
    from src.tools.sc_tools import get_demand_forecast
    result = get_demand_forecast("SKU-0001")
    assert "product_id"  in result
    assert "avg_demand"  in result
    assert "total_28d"   in result
    assert "forecast"    in result
    assert len(result["forecast"]) == 28


def test_mock_forecast_product_id_passed():
    from src.tools.sc_tools import get_demand_forecast
    result = get_demand_forecast("SKU-0042")
    assert result["product_id"] == "SKU-0042"


def test_mock_risk_alerts_returns_list():
    from src.tools.sc_tools import get_risk_alerts
    alerts = get_risk_alerts()
    assert isinstance(alerts, list)
    assert len(alerts) > 0
    assert "supplier_id" in alerts[0]
    assert "risk_score"  in alerts[0]


def test_mock_erp_query_returns_answer():
    from src.tools.erp_tools import query_erp, format_erp_answer
    result = query_erp("What is the stock for SKU-0001?")
    assert "answer"  in result
    assert "sources" in result
    answer = format_erp_answer(result)
    assert len(answer) > 0


def test_format_forecast_summary():
    from src.tools.sc_tools import format_forecast_summary
    fc = {"product_id": "SKU-0001", "avg_demand": 158, "total_28d": 4438}
    summary = format_forecast_summary(fc)
    assert "SKU-0001" in summary
    assert "158"      in summary


def test_format_risk_summary():
    from src.tools.sc_tools import format_risk_summary
    alerts = [
        {"supplier_id": "SUP-0001", "supplier_name": "Test GmbH", "risk_score": 0.55}
    ]
    summary = format_risk_summary(alerts)
    assert "SUP-0001" in summary


def test_classify_extracts_sku():
    from src.graph.workflow import classify_query, AgentState
    state = AgentState(
        query         = "Should we order more SKU-0025?",
        product_id    = "",
        forecast_data = "",
        risk_data     = "",
        erp_data      = "",
        synthesis     = "",
        decision      = "",
        confidence    = "",
        reasoning     = "",
        trace         = []
    )
    result = classify_query(state)
    assert result["product_id"] == "SKU-0025"