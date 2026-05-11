# Day 08 Lab Report

## 1. Team / student

- Name: Lại Gia Khánh
- Repo/commit: https://github.com/LaiKhanh/2A202600375_Lai_Gia_Khanh_Day23_Track3
- Date: 2026-05-11

## 2. Architecture

- **Graph builder**: [src/langgraph_agent_lab/graph.py](src/langgraph_agent_lab/graph.py) — composes nodes and conditional edges into a `StateGraph`.
- **Node implementations**: [src/langgraph_agent_lab/nodes.py](src/langgraph_agent_lab/nodes.py) — small reducer functions for `intake`, `classify`, `tool`, `evaluate`, `retry`, `risky_action`, `approval` (mock), `clarify`, `answer`, `dead_letter`, and `finalize`.
- **Routing logic**: [src/langgraph_agent_lab/routing.py](src/langgraph_agent_lab/routing.py) — maps `route`, `evaluation_result`, and `approval` to next-node names.
- **State schema**: [src/langgraph_agent_lab/state.py](src/langgraph_agent_lab/state.py) — typed `AgentState` and `Scenario` models with `initial_state()`.
- **Persistence (starter)**: [src/langgraph_agent_lab/persistence.py](src/langgraph_agent_lab/persistence.py) — checkpointer factory; starter defaults to in-memory for repeatable grading runs.

High-level flow (implemented):

START → `intake` → `classify` → {`answer`, `tool`, `clarify`, `risky_action`, `retry`} → `evaluate`/`approval` → `finalize` → END

Nodes return partial state updates; the graph composes them according to the append vs overwrite reducer semantics declared in the state schema.

## 3. State schema

| Field | Reducer | Why |
|---|---|---|
| messages | append | audit conversation/events |
| route | overwrite | current route only |
| tool_results | append | tool call evidence |
| errors | append | transient failures |
| events | append | audit log |

## 4. Scenario results

| Scenario | Expected route | Actual route | Success | Retries | Interrupts |
|---|---|---|---:|---:|---:|
| S01_simple | simple | simple | ✅ | 0 | 0 |
| S02_tool | tool | tool | ✅ | 0 | 0 |
| S03_missing | missing_info | missing_info | ✅ | 0 | 0 |
| S04_risky | risky | risky | ✅ | 0 | 1 |
| S05_error | error | error | ✅ | 3 | 0 |
| S06_delete | risky | risky | ✅ | 0 | 1 |
| S07_dead_letter | error | error | ✅ | 1 | 0 |

## Metrics summary

- Total scenarios: 7
- Success rate: 100.00%
- Average nodes visited: 6.57
- Total retries: 4
- Total interrupts: 2

## 5. Failure analysis

- **Transient tool failures** — the graph retries bounded times and escalates to `dead_letter` on exhaustion. Recommendation: add backoff and circuit-breaker.
- **Persistent outages** — escalate to human review via `dead_letter`; recommendation: add alerting and automated ticket creation.
- **Missing information** — `clarify` node prevents hallucination; recommendation: add a response loop to re-invoke the graph when a user answers.
- **Risky actions** — require HITL; currently mocked. Recommendation: implement authenticated approval UI and audit trail.
- **State loss** — in-memory saver does not survive crashes. Recommendation: enable persistent checkpointer (SQLite/Postgres) and add crash-resume tests.

## 6. Persistence / recovery evidence

Current status: in-memory checkpointer (starter default). To demonstrate crash-recovery:

1. Configure `configs/lab.yaml` to use a persistent saver (e.g., `checkpointer: sqlite` and `database_url: outputs/checkpoints.db`).
2. Run a scenario and kill the process mid-execution (or insert a sleep in a node for demo).
3. Re-run the same `thread_id` to confirm resume from the last checkpoint.

This demonstration was not included in the submission but is straightforward to add using the existing checkpointer factory.

## 7. Extension work

Describe any extra features implemented (SQLite, time travel, fan-out, diagram).

## 8. Improvement plan

1. Implement file-backed or native `interrupt()` HITL and an approval UI with authentication and audit metadata.
2. Add SQLite-based checkpointer, write integration tests that simulate kill-and-resume, and include DB evidence in the report.
3. Replace the `evaluate_node` heuristic with a judge layer (LLM or schema validator) for robust retry decisions.
4. Make `tool_node` idempotent and return structured tool results for safer evaluation.
5. Add metrics/alerts for dead-letter events, approval latency, and retry storms.
