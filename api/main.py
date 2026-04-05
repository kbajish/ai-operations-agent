import os
import mlflow
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.graph.workflow import run_agent

load_dotenv()

app = FastAPI(
    title       = "AI Operations Agent API",
    description = "Multi-agent procurement decision support using LangGraph",
    version     = "1.0.0"
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


@app.get("/agent/health")
def health():
    return {"status": "ok", "version": "1.0.0", "agent": "langgraph"}


@app.post("/agent/query", response_model=QueryResponse)
def agent_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        mlflow.set_experiment("operations-agent")

        with mlflow.start_run(run_name="procurement_agent"):
            mlflow.log_param("query", req.query[:200])

            result = run_agent(req.query)

            mlflow.log_param("product_id", result["product_id"])
            mlflow.log_param("decision",   result["decision"])
            mlflow.log_metric("confidence", result["confidence"])
            mlflow.log_metric("trace_steps", len(result["trace"]))

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