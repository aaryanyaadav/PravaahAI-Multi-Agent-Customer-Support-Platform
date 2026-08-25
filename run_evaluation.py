# run_evaluation.py
"""
Evaluation Runner for Customer Support Multi-Agent AI System.
Evaluates:
- Routing Accuracy (%)
- Answer Accuracy / Keyword Presence (%)
- Escalation Accuracy (%)
- Ticket Creation / Suppression Accuracy (%)
"""

import json
import os
import sys
import uuid
from typing import Dict, Any

# Ensure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from src.agents.orchestrator import build_orchestrator_graph

def run_evaluation(limit: int = None):
    dataset_path = "evaluation_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found. Please generate it first.")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    if limit:
        dataset = dataset[:limit]

    print(f"\n=======================================================")
    print(f"STARTING EVALUATION BENCHMARK ON {len(dataset)} QUERIES")
    print(f"=======================================================\n")

    app = build_orchestrator_graph()

    results = []
    category_stats = {}

    routing_correct = 0
    escalation_correct = 0
    ticket_correct = 0
    answer_correct = 0

    for idx, item in enumerate(dataset, start=1):
        query = item["query"]
        expected_agent = item["expected_primary_agent"]
        expected_esc = item["expected_escalation"]
        expected_tkts = item["expected_ticket_created"]
        keywords = item.get("expected_answer_keywords", [])
        category = item.get("category", "general")

        if category not in category_stats:
            category_stats[category] = {"total": 0, "routing": 0, "escalation": 0, "ticket": 0, "answer": 0}
        category_stats[category]["total"] += 1

        session_id = str(uuid.uuid4())
        initial_state = {
            "user_query": query,
            "session_id": session_id,
            "customer_context": None,
            "crm_context": None,
            "billing_context": None,
            "ticket_context": None,
            "knowledge_context": None,
            "refund_context": None,
            "agent_outputs": {},
            "current_agent": "load_memory",
            "final_response": None,
            "support_attempts": 0,
            "confidence_score": 1.0,
            "escalation_required": False,
            "escalation_reason": None,
            "ticket_id": None,
            "session_status": "active",
            "routing_steps": []
        }

        try:
            res = app.invoke(initial_state)
            
            # Determine actual routed agents from execution steps
            actual_agents = []
            for step in res.get("routing_steps", []):
                if step.get("step") == "agent_execution" and step.get("details"):
                    actual_agents.append(step["details"].get("agent_name"))
                elif step.get("step") == "routing_decision" and step.get("details"):
                    actual_agents.append(step["details"].get("next_agent"))
                elif step.get("step") == "input_guardrail" and step.get("details", {}).get("conversational"):
                    actual_agents.append("input_guard")
                elif step.get("step") == "input_guardrail" and not step.get("details", {}).get("safe"):
                    actual_agents.append("input_guard")

            actual_primary = actual_agents[0] if actual_agents else "knowledge"
            actual_esc = bool(res.get("escalation_required"))
            actual_tkts = 1 if res.get("ticket_id") else 0
            final_resp = res.get("final_response") or ""

            # Check accuracies
            r_match = (expected_agent in actual_agents) or (actual_primary == expected_agent)
            e_match = (actual_esc == expected_esc)
            t_match = (actual_tkts == expected_tkts)
            
            # Keyword/Fact matching
            if keywords:
                matched_kw = sum(1 for kw in keywords if kw.lower() in final_resp.lower())
                a_match = (matched_kw / len(keywords)) >= 0.5
            else:
                a_match = len(final_resp.strip()) > 10

            if r_match:
                routing_correct += 1
                category_stats[category]["routing"] += 1
            if e_match:
                escalation_correct += 1
                category_stats[category]["escalation"] += 1
            if t_match:
                ticket_correct += 1
                category_stats[category]["ticket"] += 1
            if a_match:
                answer_correct += 1
                category_stats[category]["answer"] += 1

            status_sym = "[PASS]" if (r_match and e_match and t_match) else "[WARN]"
            print(f"[{idx:03d}/{len(dataset):03d}] {status_sym} Query: '{query[:45]}...'")
            print(f"        Routing: expected={expected_agent}, actual={actual_primary} -> {'PASS' if r_match else 'FAIL'}")
            print(f"        Escalation: expected={expected_esc}, actual={actual_esc} | Tickets: expected={expected_tkts}, actual={actual_tkts}")

        except Exception as e:
            print(f"[{idx:03d}/{len(dataset):03d}] [FAIL] Query: '{query}' -> Exception: {e}")

    total = len(dataset)
    r_acc = (routing_correct / total) * 100
    e_acc = (escalation_correct / total) * 100
    t_acc = (ticket_correct / total) * 100
    a_acc = (answer_correct / total) * 100

    print("\n" + "="*60)
    print("                 BENCHMARK EVALUATION SUMMARY")
    print("="*60)
    print(f"Total Evaluated Queries: {total}")
    print(f"1. Routing Accuracy:     {r_acc:.1f}% ({routing_correct}/{total})")
    print(f"2. Escalation Accuracy:  {e_acc:.1f}% ({escalation_correct}/{total})")
    print(f"3. Ticket Accuracy:      {t_acc:.1f}% ({ticket_correct}/{total})")
    print(f"4. Answer/Fact Accuracy: {a_acc:.1f}% ({answer_correct}/{total})")
    print("="*60)

    print("\nCategory-wise Breakdown:")
    print(f"{'Category':<18} | {'Count':<5} | {'Routing':<8} | {'Escalation':<10} | {'Ticket':<8} | {'Answer':<8}")
    print("-" * 75)
    for cat, s in category_stats.items():
        c_tot = s["total"]
        print(f"{cat:<18} | {c_tot:<5} | {s['routing']/c_tot*100:>6.1f}% | {s['escalation']/c_tot*100:>9.1f}% | {s['ticket']/c_tot*100:>7.1f}% | {s['answer']/c_tot*100:>7.1f}%")
    print("="*60 + "\n")

if __name__ == "__main__":
    limit_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_evaluation(limit=limit_arg)
