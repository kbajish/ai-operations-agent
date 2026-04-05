import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title = "AI Operations Agent",
    page_icon  = "🤖",
    layout     = "wide"
)

st.title("🤖 AI Operations Agent — Procurement Decision Support")
st.caption("LangGraph multi-agent system with Supply Chain + ERP intelligence")

# ── Initialize session state ──────────────────────────────────────
if "last_result"    not in st.session_state:
    st.session_state["last_result"]    = None
if "current_query"  not in st.session_state:
    st.session_state["current_query"]  = ""
if "input_counter"  not in st.session_state:
    st.session_state["input_counter"]  = 0

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Sample Queries")
    samples = [
        "Should we increase our order for SKU-0001 given current supplier risks?",
        "What is the procurement status for SKU-0005?",
        "Should we place an emergency order for SKU-0010?",
        "Evaluate procurement risk for SKU-0025.",
        "Is SKU-0038 at risk of stockout?",
    ]
    for s in samples:
        if st.button(s, use_container_width=True):
            st.session_state["current_query"] = s
            st.session_state["input_counter"] += 1

    st.markdown("---")
    if st.button("Check API health"):
        try:
            r = requests.get(f"{API_URL}/agent/health", timeout=3)
            st.success(f"API online — {r.json()}")
        except Exception:
            st.error("API not reachable")

# ── Query input ───────────────────────────────────────────────────
st.subheader("Procurement Query")

query = st.text_area(
    "Enter your procurement question:",
    value       = st.session_state["current_query"],
    height      = 80,
    placeholder = "e.g. Should we increase our order for SKU-0001?",
    key         = f"query_area_{st.session_state['input_counter']}"
)

run_clicked = st.button("Run Agent", type="primary")

if run_clicked and query.strip():
    st.session_state["current_query"] = query
    with st.spinner("Agent is reasoning... (this may take 60-90 seconds)"):
        try:
            resp   = requests.post(
                f"{API_URL}/agent/query",
                json    = {"query": query},
                timeout = 180
            )
            st.session_state["last_result"] = resp.json()
        except Exception as e:
            st.error(f"Error: {e}")

# ── Results ───────────────────────────────────────────────────────
if st.session_state["last_result"]:
    result = st.session_state["last_result"]

    st.markdown("---")

    decision = result.get("decision", "").upper()
    if decision == "BUY":
        st.success(f"## Decision: {decision}")
    elif decision == "ESCALATE":
        st.error(f"## Decision: {decision}")
    else:
        st.warning(f"## Decision: {decision}")

    if result.get("error"):
        st.error(f"⚠️ {result['error']}")
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Decision",   result.get("decision",   "—"))
    col2.metric("Confidence", f"{result.get('confidence', 0.0):.0%}")
    col3.metric("Product",    result.get("product_id", "—"))

    st.subheader("Reasoning")
    st.info(result.get("reasoning", ""))

    st.subheader("Procurement Briefing")
    st.write(result.get("synthesis", ""))

    st.markdown("---")
    st.subheader("Agent Reasoning Trace")

    NODE_LABELS = {
        "classify":   "Query Classifier",
        "sc_agent":   "Supply Chain Analyst",
        "erp_agent":  "ERP Business Analyst",
        "synthesise": "Senior Procurement Analyst",
        "decide":     "Procurement Decision Maker"
    }
    NODE_COLORS = {
        "classify":   "🔵",
        "sc_agent":   "🟢",
        "erp_agent":  "🟡",
        "synthesise": "🟠",
        "decide":     "🔴"
    }

    for i, step in enumerate(result.get("trace", [])):
        node  = step.get("node", "")
        label = NODE_LABELS.get(node, node)
        icon  = NODE_COLORS.get(node, "⚪")
        with st.expander(
            f"{icon} Step {i+1}: {label}",
            expanded = (i == len(result["trace"]) - 1)
        ):
            st.text(step.get("output", ""))