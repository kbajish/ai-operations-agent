import os
import threading
import mlflow
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from dotenv import load_dotenv
from src.graph.workflow import run_agent

load_dotenv()

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlruns.db"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the workflow on startup."""
    yield


app = FastAPI(
    title       = "AI Operations Agent API",
    description = "Multi-agent procurement decision support using LangGraph",
    version     = "1.0.0",
    lifespan    = lifespan,
)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query:      str
    product_id: str
    decision:   str
    confidence: float
    reasoning:  str
    synthesis:  str
    trace:      list
    error:      str


def _log_mlflow(query: str, result: dict) -> None:
    """Log to MLflow in a background daemon thread — non-blocking."""
    def _log():
        try:
            mlflow.set_experiment("operations-agent")
            with mlflow.start_run(run_name="procurement_agent"):
                mlflow.log_param("query",      query[:200])
                mlflow.log_param("product_id", result["product_id"])
                mlflow.log_param("decision",   result["decision"])
                mlflow.log_metric("confidence", result["confidence"])
                mlflow.log_metric("trace_steps", len(result["trace"]))
        except Exception:
            pass
    threading.Thread(target=_log, daemon=True).start()


@app.get("/agent/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "agent": "langgraph"}


@app.post("/agent/query", response_model=QueryResponse)
async def agent_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        result = await run_in_threadpool(run_agent, req.query)

        # Non-blocking MLflow logging
        _log_mlflow(req.query, result)

        return QueryResponse(
            query      = result["query"],
            product_id = result["product_id"],
            decision   = result["decision"],
            confidence = result["confidence"],
            reasoning  = result["reasoning"],
            synthesis  = result["synthesis"],
            trace      = result["trace"],
            error      = result.get("error", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))