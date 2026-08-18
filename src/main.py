# src/main.py

import os
import json
import uuid
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agents.orchestrator import build_orchestrator_graph, load_session_history, get_fallback_account_id

# Initialize FastAPI Application with rich metadata
app = FastAPI(
    title="Customer Support Agentic AI API",
    description=(
        "Production-grade backend REST API for the LangGraph central customer support orchestrator. "
        "Exposes chatbot query interface, persistence logs, observability logs, and rate limiting."
    ),
    version="1.0.0",
    contact={
        "name": "Customer Support Dev Team",
        "email": "support-dev@company.com"
    }
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread-safe in-memory rate limiter
class InMemoryRateLimiter:
    def __init__(self, requests_limit: int, time_window_seconds: int):
        self.requests_limit = requests_limit
        self.time_window_seconds = time_window_seconds
        self.clients: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def check_rate_limit(self, client_ip: str) -> bool:
        """
        Returns True if request is under limit, False if rate limit is exceeded.
        """
        now = time.time()
        with self.lock:
            if client_ip not in self.clients:
                self.clients[client_ip] = [now]
                return True
            
            # Filter timestamps outside the sliding time window
            timestamps = [t for t in self.clients[client_ip] if now - t < self.time_window_seconds]
            
            if len(timestamps) >= self.requests_limit:
                self.clients[client_ip] = timestamps
                return False
            
            timestamps.append(now)
            self.clients[client_ip] = timestamps
            return True

# Limit clients to 30 requests per 60 seconds (1 minute) per IP
rate_limiter = InMemoryRateLimiter(requests_limit=30, time_window_seconds=60)

# Global rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not rate_limiter.check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Maximum 30 requests per minute allowed."}
        )
    return await call_next(request)

# Pydantic Schemas with detailed documentation
class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        description="The customer query or support message text.",
        example="Show the details of account 8c1d9bef-0ab1-4233-a643-0a32d8fb95d4"
    )
    session_id: Optional[str] = Field(
        None,
        description="Unique thread UUID for keeping conversation memory/history.",
        example="c7a0f43d-9091-4e09-a2d7-5002711c77e7"
    )
    account_id: Optional[str] = Field(
        None,
        description="Optional customer account ID UUID string context.",
        example="8c1d9bef-0ab1-4233-a643-0a32d8fb95d4"
    )

class ChatResponse(BaseModel):
    session_id: str = Field(
        ...,
        description="The conversation thread session ID.",
        example="c7a0f43d-9091-4e09-a2d7-5002711c77e7"
    )
    user_query: str = Field(
        ...,
        description="The processed/redacted customer query text.",
        example="Show the details of account 8c1d9bef-0ab1-4233-a643-0a32d8fb95d4"
    )
    final_response: str = Field(
        ...,
        description="The final support response formulation returned to the user.",
        example="Dear customer, here are your account details..."
    )
    support_attempts: int = Field(
        ...,
        description="The number of specialized support agent invocations triggered.",
        example=1
    )
    confidence_score: float = Field(
        ...,
        description="Confidence score outputted by the routing orchestrator.",
        example=0.95
    )
    escalation_required: bool = Field(
        ...,
        description="Whether this query has been escalated to L2 human executives.",
        example=False
    )
    escalation_reason: Optional[str] = Field(
        None,
        description="Details explaining why escalation was triggered, if any.",
        example="Output guardrail failed grounding validation."
    )
    ticket_id: Optional[str] = Field(
        None,
        description="The database ticket UUID generated if escalated.",
        example="9f38e8f0-ecc3-4fcb-bc50-b15358fda2b2"
    )
    routing_steps: List[Dict[str, Any]] = Field(
        ...,
        description="Observability trace detailing every routing edge, agent output, and guardrail check.",
        example=[
            {
                "step": "input_guardrail",
                "timestamp": "2026-06-25T17:24:47.953304",
                "details": {"safe": True, "reason": "Input checks passed successfully."}
            }
        ]
    )
    account_id: Optional[str] = Field(
        None,
        description="The customer account ID linked to this session.",
        example="8c1d9bef-0ab1-4233-a643-0a32d8fb95d4"
    )

class HealthResponse(BaseModel):
    status: str = Field(..., description="API operational health status.", example="ok")

# Initialize and cache LangGraph application
orchestrator_app = build_orchestrator_graph()

def handle_fallback(query: str, session_id: str, account_id: Optional[str], error_message: str) -> Dict[str, Any]:
    """
    Local rules-based fallback handler.
    Analyzes the query and generates a helpful response when the AI Orchestrator fails.
    """
    q_lower = query.lower()
    
    # Heuristics rules matching
    if "refund" in q_lower:
        response_text = (
            "Our automated refund services are temporarily offline. "
            "However, standard refunds can be processed if requested within 14 days of purchase. "
            "We have registered your refund request and escalated it to our support staff."
        )
    elif "billing" in q_lower or "invoice" in q_lower or "payment" in q_lower:
        response_text = (
            "We are unable to query billing and invoices at this moment. "
            "Please check back in a few minutes, or refer to your profile dashboard. "
            "A ticket has been opened for billing department investigation."
        )
    elif "cancel" in q_lower:
        response_text = (
            "To cancel your subscription, navigate to Billing Settings inside the workspace portal and click Cancel Plan. "
            "Your cancellation will take effect at the end of the current billing cycle."
        )
    elif "ticket" in q_lower or "status" in q_lower:
        response_text = (
            "The ticket inquiry service is temporarily offline. "
            "You can review your support tickets inside the customer console, or wait for an email update."
        )
    else:
        response_text = (
            "We are experiencing temporary service disruptions in our LLM routing layer. "
            "Your query has been registered and is being escalated directly to a customer support executive."
        )
        
    resolved_account_id = account_id or get_fallback_account_id()
    ticket_id = None
    
    # Verify query is related to proper support
    is_support = False
    import re
    support_keywords = [
        "refund", "billing", "invoice", "payment", "cancel", 
        "ticket", "status", "account", "login", "password", 
        "crm", "error", "failed", "bug", "help", "support", 
        "charge", "incorrect", "subscription", "plan", "limit"
    ]
    if any(k in q_lower for k in support_keywords):
        is_support = True
    elif len(query) > 20 and not re.match(r"^(hello|hi|hey|greetings|good morning|good afternoon|good evening|test|asdf|qwerty)\b", q_lower):
        is_support = True

    if not is_support:
        response_text = (
            "We are experiencing temporary service disruptions. "
            "Since your query does not appear to be a support request, a support ticket was not created. "
            "If you require assistance with billing, refunds, account settings, or policies, please let us know!"
        )

    # Attempt to create ticket
    if is_support:
        try:
            from database.connections import supabase
            ticket_id = str(uuid.uuid4())
            ticket_row = {
                "id": ticket_id,
                "account_id": resolved_account_id,
                "subject": "System Fallback Support Ticket",
                "priority": "Medium",
                "summary": f"System Fallback triggered. User Query: '{query}'. System Error: {error_message}",
                "status": "Open",
                "created_at": datetime.now().isoformat()
            }
            supabase.table("tickets").insert(ticket_row).execute()
        except Exception as db_err:
            print(f"Fallback Ticket Creation Failed: {db_err}")
            # Local JSON backup logging
            try:
                os.makedirs("C:/Users/Acer/.gemini/antigravity-ide/brain/cfbda447-4b01-426b-b816-15093a2a9276/scratch", exist_ok=True)
                fallback_log_path = "C:/Users/Acer/.gemini/antigravity-ide/brain/cfbda447-4b01-426b-b816-15093a2a9276/scratch/fallback_tickets.jsonl"
                with open(fallback_log_path, "a") as f:
                    f.write(json.dumps({"session_id": session_id, "query": query, "error": error_message, "timestamp": datetime.now().isoformat()}) + "\n")
            except Exception:
                pass
            
    # Attempt to save audit log
    try:
        from src.agents.orchestrator import save_conversation_log
        save_conversation_log(
            session_id=session_id,
            account_id=resolved_account_id,
            user_query=query,
            final_response=response_text,
            routing_steps=[
                {
                    "step": "fallback_handler",
                    "timestamp": datetime.now().isoformat(),
                    "details": {
                        "active": True,
                        "reason": "AI orchestrator execution failed, fallback triggered.",
                        "error": error_message
                    }
                }
            ]
        )
    except Exception as db_err:
        print(f"Fallback Audit Logging Failed: {db_err}")
        
    return {
        "session_id": session_id,
        "user_query": query,
        "final_response": response_text,
        "support_attempts": 0,
        "confidence_score": 0.0,
        "escalation_required": True,
        "escalation_reason": f"System error fallback: {error_message}",
        "ticket_id": ticket_id,
        "routing_steps": [
            {
                "step": "fallback_handler",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "active": True,
                    "reason": "AI orchestrator execution failed, fallback triggered.",
                    "error": error_message
                }
            }
        ],
        "account_id": resolved_account_id
    }

# API ROUTE HANDLERS

@app.post(
    "/api/chat",
    response_model=ChatResponse,
    summary="Submit customer support query",
    description="Routes queries through the Central Support Orchestrator or local fallback handler if the service fails.",
    responses={
        200: {"description": "Successful response from orchestrator or fallback handler."},
        429: {"description": "Too many requests. Limit is 30 requests per minute per IP address."},
        500: {"description": "Internal server execution failure."}
    }
)
async def chat(request: ChatRequest):
    """
    Submits a query to the multi-agent Central Support Orchestrator.
    Redacts PII and routes queries through CRM, Billing, Ticket, Knowledge, or Refund agents.
    """
    session_id = request.session_id or str(uuid.uuid4())
    resolved_account_id = request.account_id
    if not resolved_account_id:
        from src.agents.orchestrator import extract_account_id
        resolved_account_id = extract_account_id(request.query)
        
    # Attempt to load account_id from existing conversation messages in audit_log to preserve session context
    if not resolved_account_id and session_id:
        try:
            from database.connections import supabase
            res = supabase.table("audit_log").select("account_id, payload").execute()
            for row in res.data:
                payload = row.get("payload")
                if isinstance(payload, str):
                    try:
                        payload = json.loads(payload.replace("'", '"'))
                    except Exception:
                        pass
                if isinstance(payload, dict) and payload.get("session_id") == session_id:
                    resolved_account_id = row.get("account_id")
                    if resolved_account_id:
                        break
        except Exception as e:
            print(f"Error restoring account ID from session history: {e}")

    if not resolved_account_id:
        resolved_account_id = get_fallback_account_id()

    try:
        customer_context = None
        if resolved_account_id:
            customer_context = {"id": resolved_account_id, "account_id": resolved_account_id}
            
        initial_state = {
            "user_query": request.query,
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
        
        result = orchestrator_app.invoke(initial_state)
        
        return ChatResponse(
            session_id=result.get("session_id"),
            user_query=result.get("user_query"),
            final_response=result.get("final_response") or "No response generated.",
            support_attempts=result.get("support_attempts", 0),
            confidence_score=result.get("confidence_score", 1.0),
            escalation_required=result.get("escalation_required", False),
            escalation_reason=result.get("escalation_reason"),
            ticket_id=result.get("ticket_id"),
            routing_steps=result.get("routing_steps", []),
            account_id=resolved_account_id
        )
    except Exception as e:
        print(f"AI Orchestrator invocation failed. Activating fallback: {e}")
        fallback_res = handle_fallback(
            query=request.query,
            session_id=session_id,
            account_id=resolved_account_id,
            error_message=str(e)
        )
        return ChatResponse(**fallback_res)

@app.get(
    "/api/history/{session_id}",
    summary="Retrieve session history",
    description="Loads message history matching the session ID and optional account ID from Supabase persistence.",
    responses={
        200: {"description": "Session history retrieved successfully."},
        429: {"description": "Rate limit exceeded."},
        500: {"description": "Internal database or server error."}
    }
)
async def get_history(session_id: str, account_id: Optional[str] = None):
    """
    Retrieves chronological message history for the given session ID.
    """
    try:
        resolved_acc = account_id
        if not resolved_acc:
            try:
                from database.connections import supabase
                res = supabase.table("audit_log").select("account_id, payload").execute()
                for row in res.data:
                    payload = row.get("payload")
                    if isinstance(payload, str):
                        try:
                            payload = json.loads(payload.replace("'", '"'))
                        except Exception:
                            pass
                    if isinstance(payload, dict) and payload.get("session_id") == session_id:
                        resolved_acc = row.get("account_id")
                        if resolved_acc:
                            break
            except Exception:
                pass
        
        history = load_session_history(session_id, resolved_acc)
        return {"session_id": session_id, "history": history, "account_id": resolved_acc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/api/ping",
    summary="Network ping",
    description="Simple network connectivity check. Returns pong.",
    responses={200: {"description": "Ping successful."}}
)
async def ping():
    """
    Returns pong to check backend service reachability.
    """
    return {"ping": "pong"}

@app.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns API service health status.",
    responses={200: {"description": "Service is healthy."}}
)
async def health():
    """
    Verifies that the service is running and healthy.
    """
    return HealthResponse(status="ok")

from datetime import timedelta

@app.get(
    "/api/dashboard/stats",
    summary="Retrieve operational metrics for dashboard",
    description="Calculates counts for open tickets, total chats, escalations, and AI resolutions filtered by a number of days."
)
async def get_dashboard_stats(days: Optional[int] = None):
    """
    Fetches real conversation telemetry and database tickets data from Supabase.
    """
    try:
        from database.connections import supabase
        
        # Determine start date
        start_date = None
        if days is not None and days > 0:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Query tickets from Supabase
        tickets_query = supabase.table("tickets").select("*")
        if start_date:
            tickets_query = tickets_query.gte("created_at", start_date)
        tickets_res = tickets_query.execute()
        tickets_data = tickets_res.data or []

        # Query audit_log from Supabase
        audit_query = supabase.table("audit_log").select("*").eq("action_type", "conversation_message")
        if start_date:
            audit_query = audit_query.gte("timestamp", start_date)
        audit_res = audit_query.execute()
        audit_data = audit_res.data or []

        # Calculate metrics
        total_tickets = len(tickets_data)
        active_tickets = sum(1 for t in tickets_data if t.get("status") == "Open")
        deactive_tickets = sum(1 for t in tickets_data if t.get("status") != "Open")
        total_chats = len(audit_data)

        # Sum up tokens used in all filtered chats
        total_tokens = 0
        for row in audit_data:
            payload = row.get("payload")
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    try:
                        payload = json.loads(payload.replace("'", '"'))
                    except Exception:
                        pass
            if isinstance(payload, dict):
                total_tokens += int(payload.get("tokens_used") or 0)

        # Parse sessions
        sessions = {}
        for row in audit_data:
            sid = row.get("session_id")
            payload = row.get("payload")
            
            # Parse payload if string
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    try:
                        payload = json.loads(payload.replace("'", '"'))
                    except Exception:
                        pass
            
            if not sid and isinstance(payload, dict):
                sid = payload.get("session_id")
            
            if sid:
                if sid not in sessions:
                    sessions[sid] = {
                        "session_id": sid,
                        "chats_count": 0,
                        "escalated": False,
                        "agents": set(),
                        "steps": [],
                        "first_query": "",
                        "timestamp": row.get("timestamp") or datetime.now().isoformat()
                    }
                sessions[sid]["chats_count"] += 1
                if isinstance(payload, dict):
                    steps = payload.get("routing_steps") or []
                    if steps:
                        sessions[sid]["steps"] = steps
                    if payload.get("user_query") and not sessions[sid]["first_query"]:
                        sessions[sid]["first_query"] = payload.get("user_query")
                    
                    is_esc = payload.get("escalation_required") or payload.get("ticket_id") is not None
                    if is_esc:
                        sessions[sid]["escalated"] = True
                    
                    for step in steps:
                        if step.get("step") == "agent_execution" and step.get("details"):
                            agent_name = step["details"].get("agent_name")
                            if agent_name:
                                sessions[sid]["agents"].add(agent_name)

        total_conversations = len(sessions)
        escalated_conversations = sum(1 for s in sessions.values() if s["escalated"])
        ai_resolved_conversations = max(0, total_conversations - escalated_conversations)

        # Agent distribution
        agent_counts = {
            "crm": 0,
            "billing": 0,
            "ticket": 0,
            "knowledge": 0,
            "refund": 0
        }
        for s in sessions.values():
            for a in s["agents"]:
                a_clean = a.lower()
                if a_clean in agent_counts:
                    agent_counts[a_clean] += 1
                elif "crm" in a_clean:
                    agent_counts["crm"] += 1
                elif "billing" in a_clean:
                    agent_counts["billing"] += 1
                elif "ticket" in a_clean:
                    agent_counts["ticket"] += 1
                elif "know" in a_clean or "rag" in a_clean:
                    agent_counts["knowledge"] += 1
                elif "refund" in a_clean:
                    agent_counts["refund"] += 1

        # Daily trends (grouping by date)
        daily_trend_map = {}
        for row in audit_data:
            t = row.get("timestamp")
            if t:
                date_str = t[:10]
                if date_str not in daily_trend_map:
                    daily_trend_map[date_str] = {"total": 0, "escalated": 0}
                daily_trend_map[date_str]["total"] += 1
                
                # Check if this specific query message or its session was escalated
                payload = row.get("payload")
                if isinstance(payload, str):
                    try:
                        payload = json.loads(payload)
                    except Exception:
                        try:
                            payload = json.loads(payload.replace("'", '"'))
                        except Exception:
                            pass
                if isinstance(payload, dict):
                    is_esc = payload.get("escalation_required") or payload.get("ticket_id") is not None
                    if is_esc:
                        daily_trend_map[date_str]["escalated"] += 1
        
        daily_trends = [{"date": k, "total": v["total"], "escalated": v["escalated"]} for k, v in sorted(daily_trend_map.items())]

        # Top Intents
        intent_counts = {
            "Refunds": 0,
            "Billing & Invoices": 0,
            "Account & CRM": 0,
            "General Support": 0,
            "Security & Policy": 0
        }
        for s in sessions.values():
            categorized = False
            for step in s["steps"]:
                if step.get("step") == "routing_decision" and step.get("details"):
                    next_agent = step["details"].get("next_agent")
                    if next_agent == "refund":
                        intent_counts["Refunds"] += 1
                        categorized = True
                        break
                    elif next_agent == "billing":
                        intent_counts["Billing & Invoices"] += 1
                        categorized = True
                        break
                    elif next_agent == "crm":
                        intent_counts["Account & CRM"] += 1
                        categorized = True
                        break
                    elif next_agent == "ticket":
                        intent_counts["General Support"] += 1
                        categorized = True
                        break
            if not categorized:
                blocked = False
                for step in s["steps"]:
                    if step.get("step") == "input_guardrail" and step.get("details"):
                        if not step["details"].get("safe"):
                            intent_counts["Security & Policy"] += 1
                            blocked = True
                            break
                if not blocked:
                    intent_counts["General Support"] += 1

        # Format session queries list
        queries_list = []
        for s in sessions.values():
            queries_list.append({
                "session_id": s["session_id"],
                "first_query": s["first_query"] or "Empty query",
                "timestamp": s["timestamp"],
                "escalated": s["escalated"],
                "routing_steps": s["steps"]
            })
        
        # Sort queries list by timestamp descending, limit to 100
        queries_list = sorted(queries_list, key=lambda x: x["timestamp"], reverse=True)[:100]

        # Agent queries list (categorized by processing agent)
        agent_queries = {
            "Refund": [],
            "Billing": [],
            "CRM": [],
            "General Issues": [],
            "Ticket": []
        }
        for s in sessions.values():
            query_item = {
                "query": s["first_query"] or "Empty query",
                "session_id": s["session_id"],
                "routing_steps": s["steps"]
            }
            # Check agents
            agents_lower = {a.lower() for a in s["agents"]}
            if "refund" in agents_lower:
                agent_queries["Refund"].append(query_item)
            elif "billing" in agents_lower:
                agent_queries["Billing"].append(query_item)
            elif "crm" in agents_lower:
                agent_queries["CRM"].append(query_item)
            elif "ticket" in agents_lower:
                agent_queries["Ticket"].append(query_item)
            elif "knowledge" in agents_lower or "rag" in agents_lower:
                agent_queries["General Issues"].append(query_item)
            else:
                agent_queries["General Issues"].append(query_item)

        return {
            "total_tickets": total_tickets,
            "active_tickets": active_tickets,
            "deactive_tickets": deactive_tickets,
            "total_chats": total_chats,
            "total_conversations": total_conversations,
            "escalations_count": escalated_conversations,
            "ai_resolved_count": ai_resolved_conversations,
            "agent_distribution": agent_counts,
            "daily_trends": daily_trends,
            "top_intents": intent_counts,
            "queries_list": queries_list,
            "agent_queries": agent_queries,
            "tickets": tickets_data,
            "total_tokens": total_tokens
        }
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete(
    "/api/history/{session_id}",
    summary="Delete session history",
    description="Deletes all conversation events in audit_log associated with the given session ID."
)
async def delete_history(session_id: str):
    """
    Deletes all conversation audit log entries matching the session_id from Supabase.
    """
    try:
        from database.connections import supabase
        res = supabase.table("audit_log").delete().eq("payload->>session_id", session_id).execute()
        return {"session_id": session_id, "status": "deleted", "deleted_rows": len(res.data or [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Static files mounting removed to keep backend purely REST API.


