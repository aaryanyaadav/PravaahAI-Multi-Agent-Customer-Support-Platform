# state/support_state.py

from typing import TypedDict, List, Dict, Any, Optional

class SupportState(TypedDict):
    session_id: str
    user_query: str
    conversation_history: List[Dict[str, str]]
    
    # Contexts for shared memory
    customer_context: Optional[Dict[str, Any]]
    crm_context: Optional[Dict[str, Any]]
    billing_context: Optional[Dict[str, Any]]
    ticket_context: Optional[Dict[str, Any]]
    knowledge_context: Optional[Dict[str, Any]]
    refund_context: Optional[Dict[str, Any]]
    
    # Shared execution variables
    agent_outputs: Dict[str, Any]
    current_agent: str
    final_response: Optional[str]
    support_attempts: int
    confidence_score: float
    escalation_required: bool
    escalation_reason: Optional[str]
    ticket_id: Optional[str]
    session_status: str  # e.g., "active", "ended"
    routing_steps: List[Dict[str, Any]]
    tokens_used: Optional[int]