import os
import sys
import uuid

sys.path.append(os.path.abspath('.'))

from src.agents.orchestrator import build_orchestrator_graph
from src.guardrails.input_guard import validate_input

def test_input_guardrail_units():
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS FOR INPUT GUARDRAIL & INTENT CLASSIFICATION")
    print("="*60)
    
    test_cases = [
        ("Hi", "greeting", True),
        ("Hello", "greeting", True),
        ("Thanks", "gratitude", True),
        ("Okay", "acknowledgment", True),
        ("asdfgh", "gibberish", True),
        ("What can you do?", "capabilities", True),
        ("My invoice is incorrect and I need someone to investigate.", "support_query", False)
    ]
    
    all_passed = True
    for text, expected_intent, expected_conv in test_cases:
        res = validate_input(text)
        passed = (res.get("intent") == expected_intent) and (res.get("is_conversational") == expected_conv)
        status = "PASSED" if passed else "FAILED"
        if not passed:
            all_passed = False
        print(f"[{status}] Query: '{text}' -> Intent: '{res.get('intent')}', Conversational: {res.get('is_conversational')}")
        if res.get("direct_response"):
            preview = res.get("direct_response").replace("\n", " ")[:60]
            print(f"         Direct Response Preview: {preview}...")
            
    assert all_passed, "Unit tests failed!"
    print("\n>>> ALL INPUT GUARD UNIT TESTS PASSED SUCCESSFULLY! <<<\n")

def run_e2e_suppression_test():
    print("\n" + "="*60)
    print("RUNNING END-TO-END ORCHESTRATOR GRAPH TESTS")
    print("="*60)
    
    app = build_orchestrator_graph()
    
    # 1. Non-support conversational queries -> Expected 0 tickets
    non_support_queries = [
        "Hi",
        "Hello",
        "Thanks",
        "Okay",
        "asdfgh",
        "What can you do?"
    ]
    
    print("\n--- Testing Non-Support / Conversational Queries (Expected: 0 tickets) ---")
    for q in non_support_queries:
        session_id = str(uuid.uuid4())
        initial_state = {
            "user_query": q,
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
        
        result = app.invoke(initial_state)
        ticket_id = result.get("ticket_id")
        created_tickets = 1 if ticket_id else 0
        
        print(f"\nQuery: '{q}'")
        print(f"  Tickets Created: {created_tickets} (ticket_id: {ticket_id})")
        print(f"  Escalation Required: {result.get('escalation_required')}")
        print(f"  Response Preview: {result.get('final_response')[:80]}...")
        
        assert created_tickets == 0, f"Expected 0 tickets for '{q}', but got {created_tickets} (ticket_id: {ticket_id})"
        print(f"  -> PASS (0 tickets created)")

    # 2. Genuine support investigation query -> Expected 1 ticket
    support_query = "My invoice is incorrect and I need someone to investigate."
    print("\n--- Testing Genuine Support Investigation Query (Expected: 1 ticket) ---")
    
    session_id = str(uuid.uuid4())
    initial_state = {
        "user_query": support_query,
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
    
    result = app.invoke(initial_state)
    ticket_id = result.get("ticket_id")
    created_tickets = 1 if ticket_id else 0
    
    print(f"\nQuery: '{support_query}'")
    print(f"  Tickets Created: {created_tickets} (ticket_id: {ticket_id})")
    print(f"  Escalation Required: {result.get('escalation_required')}")
    print(f"  Final Response:\n{result.get('final_response')}")
    
    assert created_tickets == 1, f"Expected 1 ticket for support query, but got {created_tickets}"
    print(f"  -> PASS (1 ticket created)")
    
    print("\n" + "="*60)
    print("ALL TEST SCENARIOS COMPLETED SUCCESSFULLY WITH 100% ACCURACY!")
    print("="*60)

if __name__ == "__main__":
    test_input_guardrail_units()
    run_e2e_suppression_test()
