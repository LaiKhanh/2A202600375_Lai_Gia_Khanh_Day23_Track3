"""Routing functions for conditional edges."""

from __future__ import annotations

from .state import AgentState, Route


def route_after_classify(state: AgentState) -> str:
    """Map classified route to the next graph node.

    TODO(student): handle unknown routes safely and update tests for edge cases.
    """
    raw = state.get("route", Route.SIMPLE.value)
    # Accept either Route enum or string
    route = raw.value if isinstance(raw, Route) else str(raw or "").lower()
    mapping = {
        Route.SIMPLE.value: "answer",
        Route.TOOL.value: "tool",
        Route.MISSING_INFO.value: "clarify",
        Route.RISKY.value: "risky_action",
        Route.ERROR.value: "retry",
    }
    return mapping.get(route, "answer")


def route_after_retry(state: AgentState) -> str:
    """Decide whether to retry, fallback, or dead-letter.

    TODO(student): implement bounded retry and dead-letter routing.
    """
    try:
        attempt = int(state.get("attempt", 0))
    except Exception:
        attempt = 0
    try:
        max_attempts = int(state.get("max_attempts", 3))
    except Exception:
        max_attempts = 3

    if attempt >= max_attempts:
        return "dead_letter"
    return "tool"


def route_after_evaluate(state: AgentState) -> str:
    """Decide whether tool result is satisfactory or needs retry.

    This is the 'done?' check that enables retry loops — a key LangGraph advantage over LCEL.
    TODO(student): replace heuristic with LLM-as-judge or structured validation.
    """
    res = state.get("evaluation_result")
    if res in ("needs_retry", "retry"):
        return "retry"
    # If evaluation explicitly indicates exhaustion, go to dead-letter
    if res == "max_retry_exhausted":
        return "dead_letter"
    return "answer"


def route_after_approval(state: AgentState) -> str:
    """Continue only if approved.

    TODO(student): support reject/edit outcomes.
    """
    approval = state.get("approval") or {}
    try:
        approved = bool(approval.get("approved"))
    except Exception:
        approved = False
    return "tool" if approved else "clarify"
