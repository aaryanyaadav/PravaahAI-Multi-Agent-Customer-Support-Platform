# agents/test_orchestrator.py

import os
import sys
import uuid

# Add current directory to path
sys.path.append(os.path.abspath('.'))

from src.agents.orchestrator import build_orchestrator_graph

def run_orchestrator_test(query: str, session_id: str = None):
    if not session_id:
        session_id = str(uuid.uuid4())
        
    print(f"\n==================================================")
    print(f"QUERY: '{query}'")
    print(f"SESSION ID: {session_id}")
    print(f"==================================================")
    
    app = build_orchestrator_graph()
    
    # Initialize state
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
        "session_status": "active"
    }
    
    # Run the graph
    result = app.invoke(initial_state)
    
    print("\n--- TEST EXECUTION RESULT ---")
    print(f"Session Status: {result.get('session_status')}")
    print(f"Support Attempts: {result.get('support_attempts')}")
    print(f"Escalation Required: {result.get('escalation_required')} (Reason: {result.get('escalation_reason')})")
    if result.get("ticket_id"):
        print(f"Created Ticket ID: {result.get('ticket_id')}")
        
    print("\nFinal Response:\n" + str(result.get("final_response")))
    return result

if __name__ == "__main__":
    test_session = str(uuid.uuid4())
    
    # # Test 1: Knowledge/RAG query
    # run_orchestrator_test(
    #     query="What is the support refund policy for Nexus?",
    #     session_id=test_session
    # )
    
    # # Test 2: CRM query
    # run_orchestrator_test(
    #     query="Show the details of account 8c1d9bef-0ab1-4233-a643-0a32d8fb95d4",
    #     session_id=test_session
    # )
    
    # # Test 3: Multi-agent query (account details + billing overview)
    # run_orchestrator_test(
    #     query="Summarize account health and show latest payment spend for account 8c1d9bef-0ab1-4233-a643-0a32d8fb95d4",
    #     session_id=test_session
    # )
    
    # Test 4: Escalation query
    run_orchestrator_test(
        query="My issue is not resolved. Please connect me to a human executive supervisor immediately.",
        session_id=test_session
    )
