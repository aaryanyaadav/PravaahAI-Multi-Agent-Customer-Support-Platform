# agents/orchestrator.py

import json
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from llm.groq_client import GroqClient
from database.connections import supabase
from src.state.support_state import SupportState

# Import specialized agents
from src.agents.crm.crm_agent import CRMAgent
from src.agents.billing.billing_agent import BillingAgent
from src.agents.ticket.ticket_agent import TicketAgent
from src.agents.knowledge.knowledge_agent import KnowledgeAgent
from src.agents.refund.refund_agent import RefundAgent
from src.agents.escalation.escalation_agent import EscalationAgent

# Import Guardrails
from src.guardrails.input_guard import validate_input
from src.guardrails.output_guard import validate_output

# Initialize Groq client
client = GroqClient()

# System prompts for orchestrator
ROUTER_SYSTEM_PROMPT = """You are the Central Support Orchestrator.
Your goal is to coordinate a team of specialized support agents to resolve customer queries:
1. CRM Agent (`crm`): Handles customer profiles, accounts, subscriptions, plans, seat management, workspace information, and account health.
2. Billing Agent (`billing`): Handles invoice retrieval, invoices history, payments status, charge explanations, revenue analysis, and billing history.
3. Ticket Agent (`ticket`): Handles ticket retrieval, status, investigations, support history, and recent ticket activity.
4. Knowledge Agent (`knowledge`): Handles FAQ, policy, SLA, cancellation policy, subscription policy, refund policy, and security queries.
5. Refund Agent (`refund`): Verification of refund eligibility and refund decisions.

Analyze the user query, the conversation history, and any existing agent contexts to decide:
- `next_agent`: The agent ID to run next. Choose one of: "crm", "billing", "ticket", "knowledge", "refund", "escalation", or "final_response" (if the query is fully answered or resolved).
- `confidence_score`: A float from 0.0 to 1.0 representing your confidence. If the query cannot be resolved by standard agents or is ambiguous, or if a refund needs manual review, output a score below 0.65 to trigger escalation.
- `escalation_reason`: A string explaining why escalation is needed, or null if not escalating.
- `reasoning`: Short explanation of your decision.

Important Rules:
- If the user explicitly asks for a human, support executive, agent, representative, or supervisor, set `next_agent` to "escalation" with a reason.
- If multiple agents are needed (e.g. "account health, invoices, and tickets"), plan them sequentially (e.g. first route to "crm", then to "billing" or "ticket" after CRM context is populated). Look at what is already populated in the shared memory contexts!
- If an agent (such as "crm", "billing", "ticket", "knowledge", "refund") has already run and its context is populated (non-empty), DO NOT select it as the `next_agent` again in the same query. You must route to "final_response" to formulate the answer from the gathered data.
- If the agent output already contains the necessary details to formulate the final answer, route to "final_response".

Return ONLY JSON in the following format:
{
  "next_agent": "crm" | "billing" | "ticket" | "knowledge" | "refund" | "escalation" | "final_response",
  "confidence_score": float,
  "escalation_reason": string | null,
  "reasoning": string
}
"""

RESPONSE_MERGE_PROMPT = """You are a Support Orchestrator.
Combine the outputs of the support agents to construct a helpful, polite, and cohesive final response to the user query.
Use the loaded contexts to answer the query accurately. Do not invent any facts not present in the contexts.

Query: {user_query}
CRM Agent output: {crm_context}
Billing Agent output: {billing_context}
Ticket Agent output: {ticket_context}
Knowledge Agent output: {knowledge_context}
Refund Agent output: {refund_context}

Provide a production-grade, friendly, concise, and clean plain-text support response. Do not use raw markdown markup like bold asterisks (**) or list hyphens (-). Use clean spacing or linebreaks for formatting:
"""

# Helper to get first active account ID from database for FK compliance
def get_fallback_account_id() -> str:
    try:
        res = supabase.table("accounts").select("id").limit(1).execute()
        if res.data:
            return res.data[0]["id"]
    except Exception as e:
        print(f"Error fetching fallback account: {e}")
    return "8c1d9bef-0ab1-4233-a643-0a32d8fb95d4"

# Helper function to extract account ID from query
def extract_account_id(query: str) -> str:
    match = re.search(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", query)
    return match.group(0) if match else None

# Helper to load conversation history from Supabase
def load_session_history(session_id: str, account_id: str = None) -> List[Dict[str, str]]:
    try:
        query = supabase.table("audit_log").select("*")
        if account_id:
            query = query.eq("account_id", account_id)
        res = query.execute()
        
        session_logs = []
        for row in res.data:
            payload = row.get("payload")
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload.replace("'", '"'))
                except Exception:
                    pass
            if isinstance(payload, dict) and payload.get("session_id") == session_id:
                session_logs.append((row.get("timestamp") or "", payload))
        
        session_logs.sort(key=lambda x: x[0])
        
        history = []
        for _, payload in session_logs:
            if "user_query" in payload and "final_response" in payload:
                history.append({
                    "role": "user",
                    "content": payload["user_query"]
                })
                history.append({
                    "role": "assistant",
                    "content": payload["final_response"]
                })
        return history
    except Exception as e:
        print(f"Error loading session history: {e}")
        return []

# Helper to save log
def save_conversation_log(session_id: str, account_id: str, user_query: str, final_response: str, routing_steps: list = None, tokens_used: int = 0):
    try:
        payload = {
            "session_id": session_id,
            "user_query": user_query,
            "final_response": final_response,
            "routing_steps": routing_steps or [],
            "tokens_used": tokens_used
        }
        row = {
            "account_id": account_id or get_fallback_account_id(),
            "action_type": "conversation_message",
            "agent": "orchestrator",
            "payload": payload
        }
        supabase.table("audit_log").insert(row).execute()
    except Exception as e:
        print(f"Error saving conversation log: {e}")

# LANGGRAPH NODES

def load_session_memory_node(state: SupportState) -> SupportState:
    session_id = state.get("session_id") or str(uuid.uuid4())
    state["session_id"] = session_id

    # 1. Run Input Guardrail (PII redaction, toxic content/prompt injection deflection)
    original_query = state["user_query"]
    guard_res = validate_input(state["user_query"])
    state["user_query"] = guard_res["query"]
    
    if not guard_res["safe"]:
        print(f"  [Input Guardrail] Request blocked. Reason: {guard_res['reason']}")
        state["final_response"] = f"Request blocked: {guard_res['reason']}"
        state["session_status"] = "ended"
        state["ticket_id"] = None
        state["escalation_required"] = False
        state["routing_steps"] = [{
            "step": "input_guardrail",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "safe": False,
                "reason": guard_res["reason"],
                "original_query": original_query
            }
        }]
        return state

    # Handle conversational, non-support queries (greetings, pleasantries, gibberish, capabilities) immediately
    if guard_res.get("is_conversational") and guard_res.get("direct_response"):
        print(f"  [Input Guardrail] Handled conversational intent: {guard_res.get('intent')}")
        state["final_response"] = guard_res["direct_response"]
        state["session_status"] = "ended"
        state["ticket_id"] = None
        state["escalation_required"] = False
        state["routing_steps"] = [{
            "step": "input_guardrail",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "safe": True,
                "conversational": True,
                "intent": guard_res.get("intent"),
                "reason": guard_res["reason"],
                "original_query": original_query,
                "redacted_query": guard_res["query"]
            }
        }]
        return state

    # Try to extract account ID from query if not already present
    account_id = None
    if state.get("customer_context") and isinstance(state["customer_context"], dict):
        account_id = state["customer_context"].get("account_id") or state["customer_context"].get("id")
    if not account_id:
        account_id = extract_account_id(state["user_query"])
    if not account_id:
        account_id = get_fallback_account_id()
        
    # Query database for account details
    if account_id:
        try:
            acc_res = supabase.table("accounts").select("*").eq("id", account_id).execute()
            if acc_res.data:
                state["customer_context"] = acc_res.data[0]
        except Exception as e:
            print(f"Error fetching account info: {e}")
            
    # Load conversation history
    state["conversation_history"] = load_session_history(session_id, account_id)
    
    # Initialize other required state fields
    if "agent_outputs" not in state:
        state["agent_outputs"] = {}
    if "support_attempts" not in state:
        state["support_attempts"] = 0
    if "escalation_required" not in state:
        state["escalation_required"] = False
    if "session_status" not in state:
        state["session_status"] = "active"
    if "routing_steps" not in state:
        state["routing_steps"] = []
    if "tokens_used" not in state:
        state["tokens_used"] = 0
        
    state["routing_steps"].append({
        "step": "input_guardrail",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "safe": True,
            "reason": guard_res["reason"],
            "original_query": original_query,
            "redacted_query": guard_res["query"]
        }
    })
        
    return state

def orchestrator_router_node(state: SupportState) -> SupportState:
    # Build a prompt containing current state
    history_lines = []
    for msg in state.get("conversation_history", []):
        history_lines.append(f"{msg['role'].upper()}: {msg['content']}")
    history_str = "\n".join(history_lines)

    contexts_summary = f"""CRM Context: {state.get('crm_context')}
Billing Context: {state.get('billing_context')}
Ticket Context: {state.get('ticket_context')}
Knowledge Context: {state.get('knowledge_context')}
Refund Context: {state.get('refund_context')}
"""

    prompt = f"""Conversation History:
{history_str}

Current Shared Agent Contexts:
{contexts_summary}

User Query: {state['user_query']}
Support Attempts so far: {state.get('support_attempts', 0)}
"""

    response = client.invoke(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        user_prompt=prompt
    )

    state["tokens_used"] = state.get("tokens_used", 0) + getattr(response, "tokens_used", 0)

    if not response.success:
        print(f"  [Router Node] LLM invocation failed ({response.content}). Using heuristic routing.")
        q_lower = state["user_query"].lower()
        if "investigate" in q_lower or "human" in q_lower or "representative" in q_lower or "someone" in q_lower:
            result = {
                "next_agent": "escalation",
                "confidence_score": 0.5,
                "escalation_reason": "Query requires investigation / human escalation.",
                "reasoning": "Heuristic route to escalation for investigation"
            }
        elif "invoice" in q_lower or "billing" in q_lower or "charge" in q_lower:
            result = {"next_agent": "billing", "confidence_score": 0.85, "escalation_reason": None, "reasoning": "Heuristic route to billing"}
        elif "refund" in q_lower:
            result = {"next_agent": "refund", "confidence_score": 0.85, "escalation_reason": None, "reasoning": "Heuristic route to refund"}
        elif "ticket" in q_lower:
            result = {"next_agent": "ticket", "confidence_score": 0.85, "escalation_reason": None, "reasoning": "Heuristic route to ticket"}
        elif "account" in q_lower or "user" in q_lower or "seat" in q_lower:
            result = {"next_agent": "crm", "confidence_score": 0.85, "escalation_reason": None, "reasoning": "Heuristic route to crm"}
        else:
            result = {"next_agent": "knowledge", "confidence_score": 0.8, "escalation_reason": None, "reasoning": "Heuristic route to knowledge"}
    else:
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback regex parsing
            import re
            match = re.search(r"(\{.*?\})", response.content, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(1))
                except Exception:
                    result = {"next_agent": "knowledge", "confidence_score": 0.8, "escalation_reason": None, "reasoning": "Fallback parsing"}
            else:
                result = {"next_agent": "knowledge", "confidence_score": 0.8, "escalation_reason": None, "reasoning": "Fallback parsing"}

    next_agent = result.get("next_agent") or "knowledge"
    
    # Programmatic guardrail: prevent loop by forcing final_response if agent already ran
    if next_agent == "crm" and state.get("crm_context"):
        next_agent = "final_response"
    elif next_agent == "billing" and state.get("billing_context"):
        next_agent = "final_response"
    elif next_agent == "ticket" and state.get("ticket_context"):
        next_agent = "final_response"
    elif next_agent == "knowledge" and state.get("knowledge_context"):
        next_agent = "final_response"
    elif next_agent == "refund" and state.get("refund_context"):
        next_agent = "final_response"

    state["current_agent"] = next_agent
    state["confidence_score"] = float(result.get("confidence_score", 1.0))
    print(f"  [Router Node] next_agent={state['current_agent']}, confidence={state['confidence_score']}, reasoning={result.get('reasoning')}")
    
    if result.get("escalation_reason") or state["confidence_score"] < 0.65:
        state["escalation_required"] = True
        state["escalation_reason"] = result.get("escalation_reason") or "Confidence score too low."

    # Manual human escalations checks
    q_lower = state["user_query"].lower()
    if any(k in q_lower for k in ["human", "representative", "support agent", "executive", "person", "real agent"]):
        state["escalation_required"] = True
        state["escalation_reason"] = "User explicitly requested human support."

    # Check refund manual review condition
    refund_ctx = state.get("refund_context")
    if refund_ctx and isinstance(refund_ctx, dict):
        if refund_ctx.get("manual_review_required") or "escalate" in str(refund_ctx).lower():
            state["escalation_required"] = True
            state["escalation_reason"] = refund_ctx.get("reason") or "Refund decision requires manual human review."

    if "routing_steps" not in state:
        state["routing_steps"] = []
    state["routing_steps"].append({
        "step": "routing_decision",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "next_agent": state["current_agent"],
            "confidence_score": state["confidence_score"],
            "reasoning": result.get("reasoning"),
            "escalation_required": state.get("escalation_required", False),
            "escalation_reason": state.get("escalation_reason")
        }
    })

    return state


def crm_agent_node(state: SupportState) -> SupportState:
    print("  [Agent Node] CRM Agent started...")
    agent = CRMAgent()
    ans = agent.invoke(state["user_query"], shared_context=state)
    state["crm_context"] = {"agent_output": ans}
    state["agent_outputs"]["crm"] = ans
    state["support_attempts"] += 1
    
    if "routing_steps" not in state:
        state["routing_steps"] = []
    state["routing_steps"].append({
        "step": "agent_execution",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "agent_name": "crm",
            "output": ans
        }
    })
    return state

def billing_agent_node(state: SupportState) -> SupportState:
    print("  [Agent Node] Billing Agent started...")
    agent = BillingAgent()
    ans = agent.invoke(state["user_query"], shared_context=state)
    state["billing_context"] = {"agent_output": ans}
    state["agent_outputs"]["billing"] = ans
    state["support_attempts"] += 1
    
    if "routing_steps" not in state:
        state["routing_steps"] = []
    state["routing_steps"].append({
        "step": "agent_execution",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "agent_name": "billing",
            "output": ans
        }
    })
    return state

def ticket_agent_node(state: SupportState) -> SupportState:
    print("  [Agent Node] Ticket Agent started...")
    agent = TicketAgent()
    ans = agent.invoke(state["user_query"], shared_context=state)
    state["ticket_context"] = {"agent_output": ans}
    state["agent_outputs"]["ticket"] = ans
    state["support_attempts"] += 1
    
    if "routing_steps" not in state:
        state["routing_steps"] = []
    state["routing_steps"].append({
        "step": "agent_execution",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "agent_name": "ticket",
            "output": ans
        }
    })
    return state

def knowledge_agent_node(state: SupportState) -> SupportState:
    print("  [Agent Node] Knowledge Agent started...")
    agent = KnowledgeAgent()
    ans = agent.invoke(state["user_query"], shared_context=state)
    state["knowledge_context"] = {"agent_output": ans}
    state["agent_outputs"]["knowledge"] = ans
    state["support_attempts"] += 1
    
    if "routing_steps" not in state:
        state["routing_steps"] = []
    state["routing_steps"].append({
        "step": "agent_execution",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "agent_name": "knowledge",
            "output": ans
        }
    })
    return state

def refund_agent_node(state: SupportState) -> SupportState:
    print("  [Agent Node] Refund Agent started...")
    agent = RefundAgent()
    ans = agent.invoke(state["user_query"], shared_context=state)
    state["refund_context"] = {"agent_output": ans}
    state["agent_outputs"]["refund"] = ans
    state["support_attempts"] += 1
    
    if "routing_steps" not in state:
        state["routing_steps"] = []
    state["routing_steps"].append({
        "step": "agent_execution",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "agent_name": "refund",
            "output": ans
        }
    })
    return state

def escalation_node(state: SupportState) -> SupportState:
    account_id = None
    if state.get("customer_context") and isinstance(state["customer_context"], dict):
        account_id = state["customer_context"].get("id") or state["customer_context"].get("account_id")
    if not account_id:
        account_id = extract_account_id(state["user_query"])
    if not account_id:
        account_id = get_fallback_account_id()
        
    reason = state.get("escalation_reason") or "Issue requires human assistance or maximum attempts reached."
    print(f"  [Escalation Node] Escalating. Reason: {reason}")
    
    # Store handoff summary of conversation history by running the EscalationAgent
    print("  [Escalation Node] Invoking EscalationAgent for summary...")
    agent = EscalationAgent()
    escalation_query = (
        f"Generate a human handoff summary for this unresolved request: '{state['user_query']}'. "
        f"Reason for escalation: {reason}. "
        f"Prior agent outputs gathered so far: {json.dumps(state.get('agent_outputs', {}))}."
    )
    # Get L2 summary back from EscalationAgent
    escalation_ans = agent.invoke(escalation_query, shared_context=state)
    
    # Create ticket in PostgreSQL tickets table only if it is verified as a support query
    is_support = False
    verification_reason = ""
    
    # Fast guardrail check
    guard_check = validate_input(state["user_query"])
    if guard_check.get("is_conversational"):
        is_support = False
        verification_reason = f"Identified as non-support conversational intent ({guard_check.get('intent')})."
    else:
        try:
            verify_prompt = f"""Analyze the user query to determine if it is a genuine customer support request that warrants opening a database support ticket.
A genuine support request is related to billing, invoices, discrepancies, investigations, refunds, account settings/issues, cancellation, policy questions, SLA queries, or technical issues.
Simple greetings (like "hello", "hi", "hey"), pleasantries (like "thanks", "okay"), gibberish (like "asdf"), capability questions (like "what can you do?"), or testing statements do NOT warrant a support ticket.

User Query: "{state['user_query']}"

Output ONLY a JSON object in this format:
{{
  "is_support_query": true | false,
  "reason": "explanation of your decision"
}}
"""
            res = client.invoke(
                system_prompt="You are a validation assistant. Output ONLY valid JSON.",
                user_prompt=verify_prompt
            )
            state["tokens_used"] = state.get("tokens_used", 0) + getattr(res, "tokens_used", 0)
            if res.success:
                val_data = json.loads(res.content)
                is_support = bool(val_data.get("is_support_query", False))
                verification_reason = val_data.get("reason", "")
            else:
                support_keywords = [
                    "refund", "billing", "invoice", "payment", "cancel", 
                    "ticket", "status", "account", "login", "password", 
                    "crm", "error", "failed", "bug", "help", "support", 
                    "charge", "incorrect", "subscription", "plan", "limit",
                    "investigate", "investigation", "dispute", "discrepancy",
                    "wrong", "overcharge", "executive", "representative"
                ]
                q_lower = state["user_query"].lower().strip()
                if any(k in q_lower for k in support_keywords):
                    is_support = True
                    verification_reason = "Heuristic check matched support keywords."
                elif len(state["user_query"]) > 20 and not re.match(r"^(hello|hi|hey|greetings|good morning|good afternoon|good evening|test|asdf|qwerty|thanks|okay)\b", q_lower):
                    is_support = True
                    verification_reason = "Heuristic check matched length condition."
        except Exception as err:
            print(f"Error verifying query with LLM: {err}")
            support_keywords = [
                "refund", "billing", "invoice", "payment", "cancel", 
                "ticket", "status", "account", "login", "password", 
                "crm", "error", "failed", "bug", "help", "support", 
                "charge", "incorrect", "subscription", "plan", "limit",
                "investigate", "investigation", "dispute", "discrepancy",
                "wrong", "overcharge", "executive", "representative"
            ]
            q_lower = state["user_query"].lower().strip()
            if any(k in q_lower for k in support_keywords):
                is_support = True
                verification_reason = "Heuristic check matched support keywords."
            elif len(state["user_query"]) > 20 and not re.match(r"^(hello|hi|hey|greetings|good morning|good afternoon|good evening|test|asdf|qwerty|thanks|okay)\b", q_lower):
                is_support = True
                verification_reason = "Heuristic check matched length condition."

    if is_support:
        ticket_id = str(uuid.uuid4())
        try:
            row = {
                "id": ticket_id,
                "account_id": account_id,
                "subject": "Escalated Support Ticket",
                "priority": "High",
                "summary": escalation_ans,
                "status": "Open",
                "created_at": datetime.now().isoformat()
            }
            # Insert using REST API
            supabase.table("tickets").insert(row).execute()
            state["ticket_id"] = ticket_id
        except Exception as e:
            print(f"Error creating escalation ticket in database: {e}")
            state["ticket_id"] = f"ERR-{uuid.uuid4().hex[:6].upper()}"

        state["final_response"] = (
            "We were unable to fully resolve your issue.\n"
            f"A support ticket has been created and successfully saved in the PostgreSQL 'tickets' table.\n"
            f"Ticket Number: TKT-{state['ticket_id']}\n"
            "A human support executive will contact you shortly."
        )
    else:
        print(f"  [Escalation Node] Bypassing ticket creation for non-support query: '{state['user_query']}'. Reason: {verification_reason}")
        state["ticket_id"] = None
        state["final_response"] = (
            "Since your request does not appear to be a customer support query, we did not open a database ticket.\n"
            "If you require assistance with your account, billing, cancellations, or refunds, please clarify your query."
        )
    
    if "routing_steps" not in state:
        state["routing_steps"] = []
    state["routing_steps"].append({
        "step": "escalation",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "escalation_reason": reason,
            "escalation_summary": escalation_ans,
            "ticket_id": state["ticket_id"]
        }
    })
    
    save_conversation_log(state["session_id"], account_id, state["user_query"], state["final_response"], routing_steps=state.get("routing_steps"), tokens_used=state.get("tokens_used", 0))
    state["session_status"] = "ended"
    return state

def final_response_node(state: SupportState) -> SupportState:
    # If final_response is already populated (blocked by input guardrail), skip generation
    if state.get("final_response") and state.get("session_status") == "ended":
        account_id = None
        if state.get("customer_context") and isinstance(state["customer_context"], dict):
            account_id = state["customer_context"].get("id") or state["customer_context"].get("account_id")
        if not account_id:
            account_id = get_fallback_account_id()
        save_conversation_log(state["session_id"], account_id, state["user_query"], state["final_response"], routing_steps=state.get("routing_steps"), tokens_used=state.get("tokens_used", 0))
        return state

    print("  [Final Response Node] Merging outputs and generating response...")
    # Use LLM to merge contexts and generate response
    prompt = RESPONSE_MERGE_PROMPT.format(
        user_query=state["user_query"],
        crm_context=(state.get("crm_context") or {}).get("agent_output", "N/A"),
        billing_context=(state.get("billing_context") or {}).get("agent_output", "N/A"),
        ticket_context=(state.get("ticket_context") or {}).get("agent_output", "N/A"),
        knowledge_context=(state.get("knowledge_context") or {}).get("agent_output", "N/A"),
        refund_context=(state.get("refund_context") or {}).get("agent_output", "N/A")
    )
    
    response = client.invoke(
        system_prompt="You are a professional customer support representative who answers queries in a clean, professional, concise, plain-text format. Do not use markdown styling such as bold asterisks (**) or list indicators (- or *). Use line breaks or standard capitalization for structure.",
        user_prompt=prompt
    )
    state["tokens_used"] = state.get("tokens_used", 0) + getattr(response, "tokens_used", 0)
    
    if response.success:
        generated_ans = response.content
    else:
        # Fallback synthesis directly from gathered agent outputs
        collected_parts = []
        if state.get("crm_context"):
            out = state["crm_context"].get("agent_output")
            if out and out != "N/A":
                collected_parts.append(f"CRM & Account:\n{out}")
        if state.get("billing_context"):
            out = state["billing_context"].get("agent_output")
            if out and out != "N/A":
                collected_parts.append(f"Billing & Invoices:\n{out}")
        if state.get("ticket_context"):
            out = state["ticket_context"].get("agent_output")
            if out and out != "N/A":
                collected_parts.append(f"Ticket History:\n{out}")
        if state.get("knowledge_context"):
            out = state["knowledge_context"].get("agent_output")
            if out and out != "N/A":
                collected_parts.append(f"Knowledge & Policies:\n{out}")
        if state.get("refund_context"):
            out = state["refund_context"].get("agent_output")
            if out and out != "N/A":
                collected_parts.append(f"Refund Information:\n{out}")
                
        if collected_parts:
            generated_ans = "\n\n".join(collected_parts)
        else:
            generated_ans = f"Processed request for: '{state['user_query']}'. Please ensure your GROQ_API_KEY is configured in .env for full AI response generation."
    
    # 2. Run Output Guardrail (Grounding / Hallucination detection)
    validation = validate_output(
        query=state["user_query"],
        response=generated_ans,
        crm_ctx=state.get("crm_context"),
        billing_ctx=state.get("billing_context"),
        ticket_ctx=state.get("ticket_context"),
        knowledge_ctx=state.get("knowledge_context"),
        refund_ctx=state.get("refund_context")
    )
    state["tokens_used"] = state.get("tokens_used", 0) + validation.get("tokens_used", 0)
    
    print(f"  [Output Guardrail] grounded={validation.get('grounded')}, relevant={validation.get('relevant')}, reasoning={validation.get('reasoning')}")
    
    if "routing_steps" not in state:
        state["routing_steps"] = []
    state["routing_steps"].append({
        "step": "output_guardrail",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "grounded": validation.get("grounded"),
            "relevant": validation.get("relevant"),
            "reasoning": validation.get("reasoning"),
            "generated_response": generated_ans
        }
    })
    
    if not validation.get("grounded") or not validation.get("relevant"):
        # Trigger Escalation Node
        state["escalation_required"] = True
        state["escalation_reason"] = f"Output guardrail failed validation. Reasoning: {validation.get('reasoning')}"
        print(f"  [Output Guardrail] Blocked response due to hallucination or lack of relevance. Triggering escalation...")
        return escalation_node(state)
        
    state["final_response"] = generated_ans
    
    # Save conversation log for history persistence
    account_id = None
    if state.get("customer_context") and isinstance(state["customer_context"], dict):
        account_id = state["customer_context"].get("id") or state["customer_context"].get("account_id")
    if not account_id:
        account_id = extract_account_id(state["user_query"])
    if not account_id:
        account_id = get_fallback_account_id()
        
    save_conversation_log(state["session_id"], account_id, state["user_query"], state["final_response"], routing_steps=state.get("routing_steps"), tokens_used=state.get("tokens_used", 0))
    state["session_status"] = "ended"
    return state

def check_after_load(state: SupportState) -> str:
    if state.get("session_status") == "ended" or state.get("final_response"):
        return "final_response"
    return "router"

# CONDITIONAL ROUTING EDGE

def should_route(state: SupportState) -> str:
    # If session is ended or response is already set, route directly to final_response node
    if state.get("session_status") == "ended" or state.get("final_response"):
        return "final_response"

    # If escalation requested or limits exceeded, escalate immediately
    if state.get("escalation_required") or state.get("support_attempts", 0) >= 3:
        return "escalation"
        
    agent = state.get("current_agent")
    if agent in ["crm", "billing", "ticket", "knowledge", "refund", "escalation"]:
        return agent
    
    return "final_response"

# GRAPH COMPILATION

def build_orchestrator_graph():
    graph = StateGraph(SupportState)
    
    # Register nodes
    graph.add_node("load_memory", load_session_memory_node)
    graph.add_node("router", orchestrator_router_node)
    graph.add_node("crm", crm_agent_node)
    graph.add_node("billing", billing_agent_node)
    graph.add_node("ticket", ticket_agent_node)
    graph.add_node("knowledge", knowledge_agent_node)
    graph.add_node("refund", refund_agent_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("final_response", final_response_node)
    
    # Define execution edges
    graph.set_entry_point("load_memory")
    graph.add_conditional_edges(
        "load_memory",
        check_after_load,
        {
            "router": "router",
            "final_response": "final_response"
        }
    )
    
    # Router conditional edge
    graph.add_conditional_edges(
        "router",
        should_route,
        {
            "crm": "crm",
            "billing": "billing",
            "ticket": "ticket",
            "knowledge": "knowledge",
            "refund": "refund",
            "escalation": "escalation",
            "final_response": "final_response"
        }
    )
    
    # Every agent routes back to the router
    graph.add_edge("crm", "router")
    graph.add_edge("billing", "router")
    graph.add_edge("ticket", "router")
    graph.add_edge("knowledge", "router")
    graph.add_edge("refund", "router")
    
    # Terminal edges
    graph.add_edge("escalation", END)
    graph.add_edge("final_response", END)
    
    return graph.compile()
