import os
import re
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from src.tools.sc_tools import (
    get_demand_forecast, get_risk_alerts,
    format_forecast_summary, format_risk_summary
)
from src.tools.erp_tools import query_erp, format_erp_answer

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL",    "llama3.2")


class AgentState(TypedDict):
    query:         str
    product_id:    str
    forecast_data: str
    risk_data:     str
    erp_data:      str
    synthesis:     str
    decision:      str
    confidence:    str
    reasoning:     str
    trace:         list


def get_llm():
    return OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)


def classify_query(state: AgentState) -> AgentState:
    query      = state["query"]
    product_id = "SKU-0001"
    match      = re.search(r"SKU-\d+", query)
    if match:
        product_id = match.group()
    state["product_id"] = product_id
    state["trace"].append({
        "node":   "classify",
        "output": f"Query classified. Product identified: {product_id}"
    })
    return state


def sc_analyst_node(state: AgentState) -> AgentState:
    product_id       = state["product_id"]
    forecast         = get_demand_forecast(product_id)
    alerts           = get_risk_alerts()
    forecast_summary = format_forecast_summary(forecast)
    risk_summary     = format_risk_summary(alerts)

    llm    = get_llm()
    prompt = PromptTemplate.from_template("""
You are a Supply Chain Analyst. Analyse the following data and provide
a concise 2-sentence operational assessment.

Demand forecast: {forecast}
Supplier risks: {risks}
Original query: {query}

Provide your assessment:
""")
    chain      = prompt | llm | StrOutputParser()
    assessment = chain.invoke({
        "forecast": forecast_summary,
        "risks":    risk_summary,
        "query":    state["query"]
    })

    combined = (
        f"FORECAST: {forecast_summary}\n"
        f"RISKS: {risk_summary}\n"
        f"ASSESSMENT: {assessment}"
    )
    state["forecast_data"] = combined
    state["trace"].append({"node": "sc_agent", "output": combined})
    return state


def erp_analyst_node(state: AgentState) -> AgentState:
    product_id = state["product_id"]
    question   = (
        f"What is the current stock, reorder status, "
        f"and recent orders for {product_id}?"
    )
    erp_result = query_erp(question)
    erp_answer = format_erp_answer(erp_result)

    llm    = get_llm()
    prompt = PromptTemplate.from_template("""
You are an ERP Business Analyst. Analyse the following ERP data and provide
a concise 2-sentence business context summary.

ERP data: {erp_data}
Original query: {query}

Provide your summary:
""")
    chain   = prompt | llm | StrOutputParser()
    summary = chain.invoke({
        "erp_data": erp_answer,
        "query":    state["query"]
    })

    combined = f"ERP DATA: {erp_answer}\nSUMMARY: {summary}"
    state["erp_data"] = combined
    state["trace"].append({"node": "erp_agent", "output": combined})
    return state


def synthesis_node(state: AgentState) -> AgentState:
    llm    = get_llm()
    prompt = PromptTemplate.from_template("""
You are a Senior Procurement Analyst. Synthesise the following inputs
into a unified procurement briefing in 3 sentences.

Supply Chain Analysis: {sc_data}
ERP Business Context: {erp_data}
Original Query: {query}

Unified briefing:
""")
    chain    = prompt | llm | StrOutputParser()
    briefing = chain.invoke({
        "sc_data":  state["forecast_data"],
        "erp_data": state["erp_data"],
        "query":    state["query"]
    })
    state["synthesis"] = briefing
    state["trace"].append({"node": "synthesise", "output": briefing})
    return state


def decision_node(state: AgentState) -> AgentState:
    llm    = get_llm()
    prompt = PromptTemplate.from_template("""
You are a Procurement Decision Maker. Based on the briefing below,
make a structured procurement decision.

Briefing: {briefing}
Query: {query}

Respond in this exact format:
DECISION: [BUY / HOLD / ESCALATE]
CONFIDENCE: [0.0-1.0]
REASONING: [one specific sentence explaining the decision]
ACTION: [one concrete action the procurement team should take today]
""")
    chain    = prompt | llm | StrOutputParser()
    decision = chain.invoke({
        "briefing": state["synthesis"],
        "query":    state["query"]
    })

    lines  = decision.strip().split("\n")
    parsed = {}
    for line in lines:
        if ":" in line:
            key, val = line.split(":", 1)
            parsed[key.strip()] = val.strip()

    state["decision"]   = parsed.get("DECISION",   "HOLD")
    state["confidence"] = parsed.get("CONFIDENCE", "0.5")
    state["reasoning"]  = parsed.get("REASONING",  decision)
    state["trace"].append({"node": "decide", "output": decision})
    return state


def build_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("classify",   classify_query)
    graph.add_node("sc_agent",   sc_analyst_node)
    graph.add_node("erp_agent",  erp_analyst_node)
    graph.add_node("synthesise", synthesis_node)
    graph.add_node("decide",     decision_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify",   "sc_agent")
    graph.add_edge("sc_agent",   "erp_agent")
    graph.add_edge("erp_agent",  "synthesise")
    graph.add_edge("synthesise", "decide")
    graph.add_edge("decide",     END)

    return graph.compile()


def run_agent(query: str) -> dict:
    workflow = build_workflow()
    return workflow.invoke({
        "query":         query,
        "product_id":    "",
        "forecast_data": "",
        "risk_data":     "",
        "erp_data":      "",
        "synthesis":     "",
        "decision":      "",
        "confidence":    "",
        "reasoning":     "",
        "trace":         []
    })


if __name__ == "__main__":
    query  = "Should we increase our order for SKU-0001 given current supplier risks?"
    print(f"Query: {query}\n")
    print("Running agent workflow...\n")

    result = run_agent(query)

    print(f"DECISION:   {result['decision']}")
    print(f"CONFIDENCE: {result['confidence']}")
    print(f"REASONING:  {result['reasoning']}")
    print(f"\nAgent trace ({len(result['trace'])} steps):")
    for step in result["trace"]:
        print(f"  [{step['node']}] {step['output'][:120]}...")