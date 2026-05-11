"""Report generation helper.

Generates a lightweight lab report populated from a `MetricsReport`.
The output mirrors the structure in `reports/lab_report_template.md` and
includes a scenario-level table for quick inspection.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from .metrics import MetricsReport, ScenarioMetric


def _render_scenario_table(items: Iterable[ScenarioMetric]) -> str:
    lines = ["| Scenario | Expected route | Actual route | Success | Retries | Interrupts |",
             "|---|---|---|---:|---:|---:|"]
    for m in items:
        lines.append(
            f"| {m.scenario_id} | {m.expected_route} | {m.actual_route or ''} | {'✅' if m.success else '❌'} | {m.retry_count} | {m.interrupt_count} |"
        )
    return "\n".join(lines)


def render_report(metrics: MetricsReport) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d")
    parts = [
        "# Day 08 Lab Report",
        "",
        "## 1. Team / student",
        "",
        "- Name:",
        "- Repo/commit:",
        f"- Date: {now}",
        "",
        "## 2. Architecture",
        "",
        "Describe your graph nodes, edges, state fields, and reducers.",
        "",
        "## 3. State schema",
        "",
        "| Field | Reducer | Why |",
        "|---|---|---|",
        "| messages | append | audit conversation/events |",
        "| route | overwrite | current route only |",
        "| tool_results | append | tool call evidence |",
        "| errors | append | transient failures |",
        "| events | append | audit log |",
        "",
        "## 4. Scenario results",
        "",
        _render_scenario_table(metrics.scenario_metrics),
        "",
        "## Metrics summary",
        "",
        f"- Total scenarios: {metrics.total_scenarios}",
        f"- Success rate: {metrics.success_rate:.2%}",
        f"- Average nodes visited: {metrics.avg_nodes_visited:.2f}",
        f"- Total retries: {metrics.total_retries}",
        f"- Total interrupts: {metrics.total_interrupts}",
        "",
        "## 5. Failure analysis",
        "",
        "Describe failure modes and mitigation strategies.",
        "",
        "## 6. Persistence / recovery evidence",
        "",
        "Explain how the checkpointer and thread id were used to resume runs.",
        "",
        "## 7. Extension work",
        "",
        "Describe any extra features implemented (SQLite, time travel, fan-out, diagram).",
        "",
        "## 8. Improvement plan",
        "",
        "If you had one more day, what would you productionize first?",
        "",
    ]
    return "\n".join(parts)


def write_report(metrics: MetricsReport, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(metrics), encoding="utf-8")
