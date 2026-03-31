# 🤖 AI Operations Agent

![CI](https://github.com/kbajish/ai-operations-agent/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-compose-blue)

A multi-agent procurement decision support system that orchestrates specialised AI agents using LangGraph as the state machine. When a user submits a procurement query, the system decomposes it into sequential reasoning steps across five defined agent nodes, calls the supply chain forecasting service for demand and risk data, queries the ERP intelligence service for business context, synthesises the results, and generates a structured Buy / Hold / Escalate recommendation with full reasoning trace.

This project demonstrates the architecture and agent orchestration patterns of a multi-agent procurement system. It is intended as a reference implementation and learning resource, not a deployment-ready system.

---

## 🚀 Key Features

- 🔗 LangGraph state machine — explicit nodes, conditional edges, deterministic agent flow
- 🤖 Specialised agent nodes — Supply Chain Analyst, ERP Analyst, Synthesiser, Decision Maker
- 🔧 Service tool integration — calls the supply chain forecasting service ([ai-supply-chain-forecasting](https://github.com/kbajish/ai-supply-chain-forecasting)) and ERP intelligence service ([erp-llm-intelligence-rag](https://github.com/kbajish/erp-llm-intelligence-rag))
- 📋 Structured decisions — Buy / Hold / Escalate with confidence score and reasoning chain
- 🔍 Agent trace viewer — Streamlit shows every reasoning step and tool call
- 📉 MLflow run logging — full agent trace per query
- 🧪 Mock mode — offline tool stubs for CI and demos without live services
- ⚡ FastAPI backend (`/agent/query`, `/agent/health`)
- 🐳 Docker Compose for full-stack deployment
- 🔄 GitHub Actions CI/CD

---

## 🧠 System Architecture

```
User procurement query
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

A user submits a natural language procurement query. LangGraph routes it through a defined sequence of five agent nodes. The SC Analyst node calls the supply chain forecasting service ([ai-supply-chain-forecasting](https://github.com/kbajish/ai-supply-chain-forecasting)) to retrieve 28-day demand forecasts and supplier risk alerts. The ERP Analyst node queries the ERP intelligence service ([erp-llm-intelligence-rag](https://github.com/kbajish/erp-llm-intelligence-rag)) for relevant business context such as current stock levels, open orders, and revenue metrics. The Synthesiser node combines both outputs into a unified context. The Decision node reasons over the combined data and produces a structured Buy / Hold / Escalate recommendation with a confidence score and justification.

The full reasoning trace — every node, tool call, and intermediate result — is logged to MLflow and displayed step by step in the Streamlit dashboard, providing complete transparency into the agent's decision process.

---

## 📊 Sample Interaction

**Query:** Should we increase our order for SKU-0001 given current supplier risks?

**Agent trace:**
- SC Analyst → forecast SKU-0001: 158 units/day, 10 high-risk suppliers detected
- ERP Analyst → current stock: 1,200 units, reorder point: 800 units
- Synthesiser → 28-day demand: 4,438 units, stock covers 7.6 days only

**Decision:** `BUY` — Confidence: 0.87. Increase order by 30% (5,770 units). Knorr-Bremse AG (SUP-0038) flagged as high risk — qualify alternative supplier within 14 days.

---

## 📊 Dashboard Overview

The Streamlit dashboard provides:

- 💬 Query input for natural language procurement questions
- 🔍 Step-by-step agent reasoning trace with colour-coded nodes
- 📋 Final structured recommendation panel
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
| Backend | FastAPI, Uvicorn |
| Dashboard | Streamlit |
| Experiment tracking | MLflow |
| Containerisation | Docker Compose |
| CI/CD | GitHub Actions |
| Testing | pytest |

---

## 📂 Project Structure

```
ai-operations-agent/
│
├── src/
│   ├── graph/
│   │   └── workflow.py            # LangGraph state machine — all 5 agent nodes
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
│   ├── test_tools.py              # Tool wrapper tests
│   └── test_imports.py            # CI-safe import tests
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

### 3. Start dependent services (optional — for live API mode)
```bash
# Clone and start ai-supply-chain-forecasting on port 8002
# Clone and start erp-llm-intelligence-rag on port 8001
# Or set USE_MOCK_TOOLS=true in .env to use mock mode
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
