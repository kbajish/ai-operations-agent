def test_mock_tools_imports():
    from src.tools.mock_tools import (
        mock_get_forecast, mock_get_risk_alerts,
        mock_get_supplier_risk, mock_erp_query
    )
    assert callable(mock_get_forecast)
    assert callable(mock_get_risk_alerts)
    assert callable(mock_get_supplier_risk)
    assert callable(mock_erp_query)


def test_sc_tools_imports():
    from src.tools.sc_tools import (
        get_demand_forecast, get_risk_alerts,
        format_forecast_summary, format_risk_summary
    )
    assert callable(get_demand_forecast)
    assert callable(get_risk_alerts)


def test_erp_tools_imports():
    from src.tools.erp_tools import query_erp, format_erp_answer
    assert callable(query_erp)
    assert callable(format_erp_answer)


def test_workflow_imports():
    from src.graph.workflow import build_workflow, run_agent
    assert callable(build_workflow)
    assert callable(run_agent)


def test_workflow_builds():
    from src.graph.workflow import build_workflow
    workflow = build_workflow()
    assert workflow is not None