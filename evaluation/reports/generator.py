import json
import os
from datetime import datetime
from typing import List, Dict, Any

from evaluation.metrics.routing_metrics import compute_routing_metrics
from evaluation.metrics.answer_metrics import compute_answer_metrics
from evaluation.metrics.escalation_metrics import compute_escalation_metrics
from evaluation.metrics.latency_metrics import compute_latency_metrics

def generate_evaluation_reports(results: List[Dict[str, Any]], output_dir: str = None) -> str:
    """
    Computes all benchmark metrics and generates:
    - raw_results.json
    - summary_metrics.json
    - evaluation_report.md
    Returns the path to the generated run directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "runs", f"run_{timestamp}")

    os.makedirs(output_dir, exist_ok=True)

    # 1. Compute aggregate metrics
    routing_stats = compute_routing_metrics(results)
    answer_stats = compute_answer_metrics(results)
    escalation_stats = compute_escalation_metrics(results)
    latency_stats = compute_latency_metrics(results)

    # Category breakdown
    categories = sorted(list(set(r.get("category", "general") for r in results)))
    category_summary = {}
    for cat in categories:
        cat_items = [r for r in results if r.get("category") == cat]
        tot = len(cat_items)
        r_corr = sum(1 for r in cat_items if r["routing_passed"])
        e_corr = sum(1 for r in cat_items if r["escalation_passed"])
        t_corr = sum(1 for r in cat_items if r["ticket_passed"])
        a_corr = sum(1 for r in cat_items if r["answer_passed"])
        category_summary[cat] = {
            "total_queries": tot,
            "routing_accuracy": round((r_corr / tot) * 100.0, 1),
            "escalation_accuracy": round((e_corr / tot) * 100.0, 1),
            "ticket_accuracy": round((t_corr / tot) * 100.0, 1),
            "answer_accuracy": round((a_corr / tot) * 100.0, 1)
        }

    summary = {
        "timestamp": timestamp,
        "total_queries": len(results),
        "overall_kpis": {
            "routing_accuracy_pct": routing_stats["accuracy"],
            "escalation_accuracy_pct": escalation_stats["escalation_accuracy"],
            "ticket_accuracy_pct": escalation_stats["ticket_creation_accuracy"],
            "answer_accuracy_pct": answer_stats["accuracy"],
            "keyword_coverage_pct": answer_stats["avg_keyword_coverage"],
            "conversational_suppression_pct": escalation_stats["conversational_ticket_suppression_rate"]
        },
        "latency_and_tokens": latency_stats,
        "routing_metrics": routing_stats,
        "escalation_metrics": escalation_stats,
        "answer_metrics": answer_stats,
        "category_breakdown": category_summary
    }

    # 2. Save raw_results.json
    raw_path = os.path.join(output_dir, "raw_results.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 3. Save summary_metrics.json
    summary_path = os.path.join(output_dir, "summary_metrics.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # 4. Generate evaluation_report.md
    md_report = f"""# Customer Support Multi-Agent AI — Evaluation Report

**Run Timestamp**: `{timestamp}`  
**Total Queries Evaluated**: `{len(results)}`  
**Artifact Location**: `{output_dir}`

---

## Executive KPI Summary

| Benchmark Metric | Score | Target | Status |
| :--- | :---: | :---: | :---: |
| **Routing Accuracy** | **{routing_stats['accuracy']}%** | ≥ 95.0% | {'✅ Pass' if routing_stats['accuracy'] >= 95.0 else '⚠️ Review'} |
| **Escalation Accuracy** | **{escalation_stats['escalation_accuracy']}%** | ≥ 95.0% | {'✅ Pass' if escalation_stats['escalation_accuracy'] >= 95.0 else '⚠️ Review'} |
| **Ticket Accuracy (Suppression & Creation)** | **{escalation_stats['ticket_creation_accuracy']}%** | 100.0% | {'✅ Pass' if escalation_stats['ticket_creation_accuracy'] == 100.0 else '⚠️ Review'} |
| **Conversational Ticket Suppression** | **{escalation_stats['conversational_ticket_suppression_rate']}%** | 100.0% | {'✅ Pass' if escalation_stats['conversational_ticket_suppression_rate'] == 100.0 else '⚠️ Review'} |
| **Answer / Factual Accuracy** | **{answer_stats['accuracy']}%** | ≥ 90.0% | {'✅ Pass' if answer_stats['accuracy'] >= 90.0 else '⚠️ Review'} |
| **Average Keyword Coverage** | **{answer_stats['avg_keyword_coverage']}%** | ≥ 85.0% | {'✅ Pass' if answer_stats['avg_keyword_coverage'] >= 85.0 else '⚠️ Review'} |

---

## Latency & Token Telemetry

| Metric | Measured Value |
| :--- | :--- |
| **Median Latency (p50)** | `{latency_stats['p50_seconds']}s` |
| **90th Percentile Latency (p90)** | `{latency_stats['p90_seconds']}s` |
| **99th Percentile Latency (p99)** | `{latency_stats['p99_seconds']}s` |
| **Average Response Duration** | `{latency_stats['mean_seconds']}s` (Min: `{latency_stats['min_seconds']}s`, Max: `{latency_stats['max_seconds']}s`) |
| **Total Tokens Consumed** | `{latency_stats['total_tokens']:,}` tokens |
| **Average Tokens per Query** | `{latency_stats['avg_tokens_per_query']}` tokens |

---

## Category-wise Performance Breakdown

| Category | Queries | Routing Acc | Escalation Acc | Ticket Acc | Answer Acc |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""
    for cat, s in category_summary.items():
        md_report += f"| **{cat.upper()}** | {s['total_queries']} | {s['routing_accuracy']}% | {s['escalation_accuracy']}% | {s['ticket_accuracy']}% | {s['answer_accuracy']}% |\n"

    md_report += """
---

## Agent Routing Performance & Confusion Matrix

### Per-Agent Metrics

| Agent | Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
"""
    for agent, p in routing_stats.get("per_agent_metrics", {}).items():
        md_report += f"| **{agent}** | {p['support']} | {p['precision']}% | {p['recall']}% | {p['f1_score']}% |\n"

    # Confusion matrix
    conf = routing_stats.get("confusion_matrix", {})
    if conf:
        agents = sorted(list(conf.keys()))
        md_report += "\n### Confusion Matrix (Rows = Expected, Columns = Predicted)\n\n"
        md_report += "| Expected \\ Actual | " + " | ".join(agents) + " |\n"
        md_report += "| :--- | " + " | ".join([":---:" for _ in agents]) + " |\n"
        for exp in agents:
            row_vals = [str(conf[exp].get(act, 0)) for act in agents]
            md_report += f"| **{exp}** | " + " | ".join(row_vals) + " |\n"

    # Failures / Warnings table if any
    failed_items = [r for r in results if not r["overall_passed"]]
    if failed_items:
        md_report += f"""
---

## Divergent / Warning Scenarios ({len(failed_items)} items)

| ID | Query | Expected Agent | Actual Agent | Esc (Exp/Act) | Tkts (Exp/Act) | Note |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
"""
        for r in failed_items[:15]:
            note = []
            if not r["routing_passed"]:
                note.append(f"Route: {r['expected_agent']} != {r['actual_primary_agent']}")
            if not r["escalation_passed"]:
                note.append(f"Esc: {r['expected_escalation']} != {r['actual_escalation']}")
            if not r["ticket_passed"]:
                note.append(f"Tkt: {r['expected_tickets']} != {r['actual_tickets']}")
            if not r["answer_passed"]:
                note.append(f"Kw Cov: {int(r['keyword_coverage']*100)}%")
            md_report += f"| {r['query_id']} | `{r['query'][:35]}...` | `{r['expected_agent']}` | `{r['actual_primary_agent']}` | {r['expected_escalation']}/{r['actual_escalation']} | {r['expected_tickets']}/{r['actual_tickets']} | {', '.join(note)} |\n"

    md_report += """
---
*Report generated automatically by the Customer Support Agentic AI Evaluation Framework.*
"""

    report_path = os.path.join(output_dir, "evaluation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    return output_dir
