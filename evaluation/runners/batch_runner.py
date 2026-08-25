import time
import uuid
from typing import List, Dict, Any, Optional

from src.agents.orchestrator import build_orchestrator_graph

class BatchEvaluator:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.app = build_orchestrator_graph()

    def evaluate_single_query(self, item: Dict[str, Any], query_index: int = 1, total_queries: int = 1) -> Dict[str, Any]:
        query = item["query"]
        expected_agent = item["expected_primary_agent"]
        expected_esc = item["expected_escalation"]
        expected_tkts = item["expected_ticket_created"]
        keywords = item.get("expected_answer_keywords", [])
        category = item.get("category", "general")
        target_acc = item.get("target_account_id")

        session_id = str(uuid.uuid4())
        customer_context = None
        if target_acc:
            customer_context = {"id": target_acc, "account_id": target_acc}

        initial_state = {
            "user_query": query,
            "session_id": session_id,
            "customer_context": customer_context,
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

        start_time = time.time()
        error_msg = None
        res = {}
        try:
            res = self.app.invoke(initial_state)
        except Exception as e:
            error_msg = str(e)
            if self.verbose:
                print(f"  [Evaluator Exception on Query {query_index}]: {e}")
        duration = time.time() - start_time

        # Extract routing sequence
        actual_agents = []
        routing_steps = res.get("routing_steps", [])
        for step in routing_steps:
            if step.get("step") == "agent_execution" and step.get("details"):
                actual_agents.append(step["details"].get("agent_name"))
            elif step.get("step") == "routing_decision" and step.get("details"):
                actual_agents.append(step["details"].get("next_agent"))
            elif step.get("step") == "input_guardrail":
                details = step.get("details", {})
                if details.get("conversational") or not details.get("safe"):
                    actual_agents.append("input_guard")

        actual_primary = actual_agents[0] if actual_agents else "knowledge"
        actual_esc = bool(res.get("escalation_required"))
        actual_tkts = 1 if res.get("ticket_id") else 0
        final_resp = res.get("final_response") or ""
        tokens_used = res.get("tokens_used", 0)

        # 1. Routing check
        routing_passed = (expected_agent in actual_agents) or (actual_primary == expected_agent)

        # 2. Escalation check
        escalation_passed = (actual_esc == expected_esc)

        # 3. Ticket creation check
        ticket_passed = (actual_tkts == expected_tkts)

        # 4. Answer / Keyword match check
        keyword_coverage = 1.0
        if keywords:
            matched_kw = sum(1 for kw in keywords if kw.lower() in final_resp.lower())
            keyword_coverage = matched_kw / len(keywords)
            answer_passed = keyword_coverage >= 0.5
        else:
            answer_passed = len(final_resp.strip()) > 10

        overall_passed = routing_passed and escalation_passed and ticket_passed and answer_passed

        result_record = {
            "query_id": item["id"],
            "query": query,
            "category": category,
            "expected_agent": expected_agent,
            "actual_primary_agent": actual_primary,
            "actual_agent_sequence": actual_agents,
            "routing_passed": routing_passed,
            "expected_escalation": expected_esc,
            "actual_escalation": actual_esc,
            "escalation_passed": escalation_passed,
            "expected_tickets": expected_tkts,
            "actual_tickets": actual_tkts,
            "ticket_passed": ticket_passed,
            "expected_keywords": keywords,
            "keyword_coverage": round(keyword_coverage, 3),
            "answer_passed": answer_passed,
            "overall_passed": overall_passed,
            "final_response": final_resp,
            "tokens_used": tokens_used,
            "duration_seconds": round(duration, 3),
            "error": error_msg,
            "routing_steps": routing_steps
        }

        badge = "[PASS]" if overall_passed else "[WARN]"
        print(f"[{query_index:03d}/{total_queries:03d}] {badge} Query: '{query[:42]}...' | R:{'OK' if routing_passed else 'ERR'} E:{'OK' if escalation_passed else 'ERR'} T:{'OK' if ticket_passed else 'ERR'} A:{'OK' if answer_passed else 'ERR'} ({duration:.2f}s)")

        return result_record

    def run_batch(self, dataset: List[Dict[str, Any]], limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        target_data = dataset
        if category:
            target_data = [d for d in target_data if d.get("category") == category]
        if limit:
            target_data = target_data[:limit]

        total = len(target_data)
        print(f"\n=======================================================")
        print(f"RUNNING BENCHMARK EVALUATION ({total} Queries)")
        print(f"=======================================================\n")

        results = []
        for i, item in enumerate(target_data, start=1):
            record = self.evaluate_single_query(item, query_index=i, total_queries=total)
            results.append(record)
            # Brief pacing delay to avoid aggressive rate limits
            time.sleep(0.15)

        return results
