# 🤖 AI Operations Agent

![CI](https://github.com/kbajish/ai-operations-agent/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-compose-blue)

A multi-agent procurement decision support system that orchestrates specialised AI agents using LangGraph as the state machine. When a user submits a procurement query, the system decomposes it into sequential reasoning steps across five defined agent nodes, calls the supply chain forecasting service for demand and risk data, queries the ERP intelligence service for business context, synthesises the results, and generates a structured Buy / Hold / Escalate recommendation with full reasoning trace.

Designed as a reference implementation of production-grade LLM agent orchestration patterns.

---

## 🚀 Key Features

- 🔗 LangGraph state machine — explicit nodes, conditional edges, deterministic agent flow
- 🤖 Specialised agent nodes — Supply Chain Analyst, ERP Analyst, Synthesiser, Decision Maker
- 🔧 Service tool integration — calls [ai-supply-chain-forecasting](https://github.com/kbajish/ai-supply-chain-forecasting) and [erp-llm-intelligence-rag](https://github.com/kbajish/erp-llm-intelligence-rag) as live tools
- 📋 Structured decisions — Buy / Hold / Escalate with float confidence score and reasoning chain
- 🛡️ Input validation — rejects empty, malformed, and unsafe queries before processing
- 🔒 Tool access control — agent restricted to predefined permitted tools only
- 🔄 Resilient tool calls — try/except on all external calls with safe fallback responses
- 🔍 Regex-based decision parsing — robust extraction of DECISION, CONFIDENCE, REASONING
- 🔍 Agent trace viewer — Streamlit shows every reasoning step and tool call
- 📉 MLflow run logging — full agent trace per query
- 🧪 Mock mode — offline tool stubs for CI and demos without live services
- ⚡ Async FastAPI backend — non-blocking with threadpool offloading (`/agent/query`, `/agent/health`)
- 🐳 Docker Compose for full-stack deployment
- 🔄 GitHub Actions CI/CD — 15 tests passing

---

## 🧠 System Architecture

```
User procurement query
        ↓
Input validation (length, content, unsafe pattern detection)
        ↓
LangGraph state machine
        ↓
        ├── Node 1: classify      — query classifier, extracts product ID
        ├── Node 2: sc_agent      — calls supply chain forecasting service
        │                           /forecast + /risk/alerts endpoints
        ├── Node 3: erp_agent     — calls ERP intelligence service
        │                           /query RAG endpoint
        ├── Node 4: synthesise    — combines SC + ERP context
        └── Node 5: decide        — generates Buy / Hold / Escalate decision
        ↓
api/main.py              — FastAPI (/agent/query, /agent/health)
        ↓
dashboard/app.py         — Streamlit trace viewer + recommendation panel
        ↓
MLflow                   — agent run logging
```

---

## ⚙️ How It Works

A user submits a natural language procurement query. Before entering the workflow, the query is validated for length, content, and unsafe patterns — prompt injection attempts and malformed inputs are rejected immediately. LangGraph then routes the validated query through a defined sequence of five agent nodes.

The SC Analyst node calls the supply chain forecasting service to retrieve 28-day demand forecasts and supplier risk alerts. The ERP Analyst node queries the ERP intelligence service for relevant business context such as current stock levels, open orders, and revenue metrics. The Synthesiser node combines both outputs into a unified context. The Decision node reasons over the combined data and produces a structured Buy / Hold / Escalate recommendation with a confidence score and justification.

All external tool calls are wrapped in try/except blocks with safe fallback responses — the workflow completes even if a downstream service is unavailable. Decision parsing uses regex extraction to reliably handle varying LLM output formats. The full reasoning trace is logged to MLflow and displayed step by step in the Streamlit dashboard.

---

## 📊 Sample Interaction

**Query:** Should we increase our order for SKU-0001 given current supplier risks?

**Agent trace:**
- SC Analyst → forecast SKU-0001: 158 units/day, 10 high-risk suppliers detected
- ERP Analyst → current stock: 1,200 units, reorder point: 800 units
- Synthesiser → 28-day demand: 4,438 units, stock covers 7.6 days only

**Decision:** `BUY` — Confidence: 0.87. Increase order by 30% (5,770 units). Knorr-Bremse AG (SUP-0038) flagged as high risk — qualify alternative supplier within 14 days.

---

## 📊 Evaluation Results

Evaluated against 14 test queries — 10 valid procurement queries and 4 invalid inputs designed to test rejection logic. All tests run with `USE_MOCK_TOOLS=true` via `tests/eval/run_evaluation.py`.

### Execution Metrics

| Metric | Value |
|---|---|
| Total queries tested | 14 |
| Successful API calls | 14 (100%) |
| Valid queries completed | 10 / 10 (100%) |
| Invalid queries rejected | 4 / 4 (100%) |
| Steps per valid query | 5 (fixed workflow) |
| LLM calls per valid query | 4 (sc_agent, erp_agent, synthesise, decide) |

### Decision Distribution (10 valid queries)

```
BUY        6  ██████
HOLD       6  ██████
ESCALATE   1  █
```

### Input Validation

| Query Type | Result |
|---|---|
| Empty string | Rejected — HTTP 400 (FastAPI validation) |
| Too short (`buy?`) | Rejected — workflow length check |
| Prompt injection attempt | Rejected — unsafe pattern detected |
| Oversized input (2000+ chars) | Rejected — length validation |

---

## ⚡ Performance

Measured with `USE_MOCK_TOOLS=true`, Ollama llama3.2 on CPU, Windows local environment.

| Layer | Latency |
|---|---|
| Input validation (rejected queries) | ~150–200ms |
| Full 5-step pipeline (mock tools, CPU LLM) | ~52,000–81,000ms |
| Mean end-to-end latency | ~68,000ms |

The agent executes a fixed 5-step workflow. Each valid query involves 4 sequential LLM inference calls — overall latency is entirely dominated by CPU-based LLM response time.

**Note:** With GPU inference or a cloud LLM API (e.g. Groq), each LLM call drops from ~15s to ~1–2s, reducing total pipeline latency to approximately 5–10s per query.

---

## 🔧 Implementation Notes

**Input validation** — queries are validated for minimum length (10 chars), maximum length (2000 chars), and unsafe content patterns (prompt injection, jailbreak attempts) before entering the workflow. Invalid queries are rejected immediately with a clear error message.

**Tool access control** — all tool calls go through a central `call_tool()` registry. Only tools registered in `PERMITTED_TOOLS` can be invoked — any attempt to call an unregistered function raises a `ValueError` before execution.

**Resilient tool calls** — every external service call (`get_demand_forecast`, `get_risk_alerts`, `query_erp`) is wrapped in try/except. On failure, the node returns a safe fallback response and the workflow continues to completion rather than crashing.

**Regex decision parsing** — the LLM decision output is parsed using regex patterns for `DECISION`, `CONFIDENCE`, and `REASONING` fields. This is robust to formatting variations in LLM output. Confidence is stored as a float clamped to [0.0, 1.0]. Safe defaults (HOLD, 0.5) apply if parsing fails.

**Async FastAPI endpoint** — the `/agent/query` endpoint is fully async using `run_in_threadpool` to offload the LangGraph workflow execution. This keeps the event loop free for concurrent requests. MLflow logging runs in a background daemon thread so it never adds latency to the response cycle.

---

## 📊 Dashboard Overview

The Streamlit dashboard provides:

- 💬 Query input for natural language procurement questions
- 🔍 Step-by-step agent reasoning trace with colour-coded nodes
- 📋 Final structured recommendation panel with confidence percentage
- ⚠️ Error display for rejected or failed queries
- 📉 MLflow run summary per query

---

## 📸 Dashboard

[View full dashboard screenshot](docs/dashboard_screenshot.pdf)

---

## 🛠 Tech Stack

| Layer | Tool |
|---|---|
| Orchestration | LangGraph |
| Agent nodes | LangChain + Ollama (llama3.2, local) |
| Supply chain service | [ai-supply-chain-forecasting](https://github.com/kbajish/ai-supply-chain-forecasting) |
| ERP intelligence service | [erp-llm-intelligence-rag](https://github.com/kbajish/erp-llm-intelligence-rag) |
| Backend | FastAPI (async endpoints), Uvicorn |
| Dashboard | Streamlit |
| Experiment tracking | MLflow |
| Containerisation | Docker Compose |
| CI/CD | GitHub Actions |
| Testing | pytest (15 tests) |

---

## 📂 Project Structure

```
ai-operations-agent/
│
├── src/
│   ├── graph/
│   │   └── workflow.py            # LangGraph state machine — all 5 agent nodes,
│   │                              # input validation, tool access control
│   └── tools/
│       ├── sc_tools.py            # Supply chain service tool wrappers
│       ├── erp_tools.py           # ERP intelligence service tool wrappers
│       └── mock_tools.py          # Mock tools for CI / offline demo
│
├── api/
│   └── main.py                    # FastAPI app
│
├── dashboard/
│   └── app.py                     # Streamlit trace viewer
│
├── tests/
│   ├── test_tools.py              # Robustness and validation tests (10 tests)
│   ├── test_imports.py            # CI-safe import tests (5 tests)
│   └── eval/
│       └── run_evaluation.py      # Evaluation and latency benchmark script
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions pipeline
│
├── mlruns/                        # MLflow tracking (not committed)
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.dashboard
├── .env.example
├── requirements.api.txt
├── requirements.dashboard.txt
├── requirements.dev.txt
├── AI_ACT_COMPLIANCE.md
└── README.md
```

---

## ▶️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/kbajish/ai-operations-agent.git
cd ai-operations-agent
```

### 2. Create and activate virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
```

### 3. Configure environment
```bash
cp .env.example .env
# Set USE_MOCK_TOOLS=true for offline mode (default)
# Set SC_API_URL and ERP_API_URL for live service integration
```

### 4. Start all services
```bash
docker compose up --build
```

### 5. Access services

| Service   | URL                        |
|-----------|----------------------------|
| API       | http://localhost:8000      |
| API docs  | http://localhost:8000/docs |
| Dashboard | http://localhost:8501      |
| MLflow    | http://localhost:5000      |

---

## 🧪 API Endpoints

| Method | Endpoint        | Description                                      |
|--------|-----------------|--------------------------------------------------|
| `POST` | `/agent/query`  | Run procurement agent — returns trace + decision |
| `GET`  | `/agent/health` | Health check                                     |

---

## 🧪 Tests

```bash
# Unit tests
pytest tests/ -v
# 15 passed

# Evaluation suite (requires API running)
python tests/eval/run_evaluation.py
# 14 queries — 100% success rate, 4/4 invalid queries rejected
```

---

## 🔧 Mock Mode

Set `USE_MOCK_TOOLS=true` in your `.env` file to run the agent without the supply chain and ERP services running. Mock tools return realistic synthetic responses — useful for CI, offline demos, and development.

---

## 📈 Possible Extensions

- Add the AI Security Gateway as a fourth tool for threat-aware procurement
- Human-in-the-loop approval node for high-value decisions
- LangSmith / AgentOps observability integration
- Persistent agent memory across sessions
- Streaming agent steps via WebSocket

---

## 👤 Author

Experienced IT professional with a background in development, cybersecurity, and ERP systems, with expertise in Industrial AI. Focused on building well-engineered AI systems with explainability, LLM integration, and MLOps practices.
