# EU AI Act & DSGVO Compliance Notes

## Risk classification
This system provides AI-generated procurement recommendations to support
human decision-making. It is a decision-support tool — all recommendations
require human review before execution. Under the EU AI Act, this system
is classified as limited risk.

## Transparency measures
- Every recommendation includes a full reasoning trace
- Confidence scores are provided with every decision
- Tool call inputs and outputs are logged for auditability
- Users are informed they are interacting with an AI agent

## Human oversight
- All Buy / Hold / Escalate decisions require human approval
- No automated procurement actions are taken by the system
- MLflow logs every agent run for post-hoc review

## Model governance
- LLM model version is logged in every MLflow run
- Agent workflow version is tracked via Git commit hash