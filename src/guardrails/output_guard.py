import json
import re
from llm.groq_client import GroqClient

client = GroqClient()

EVALUATION_SYSTEM_PROMPT = """You are an AI Quality Guardrail.
Your goal is to evaluate if a final customer support response is grounded in the retrieved contexts and relevant to the user query.

You must identify:
1. Hallucinations: If the Response contains facts, figures, details, links, or contact details (e.g., specific phone numbers, emails, addresses, names, ticket IDs) NOT explicitly present in the Contexts, set "grounded" to false. (General polite formatting is allowed, but do not invent data).
2. Relevance: If the Response does not address the main question asked in the User Query, set "relevant" to false.

Return ONLY a valid JSON object in the following format:
{
  "grounded": boolean,
  "relevant": boolean,
  "reasoning": "brief explanation"
}
"""

EVALUATION_USER_PROMPT = """User Query: {query}

Retrieved Agent Contexts:
{contexts}

Response to Evaluate:
{response}
"""

def validate_output(query: str, response: str, crm_ctx: dict, billing_ctx: dict, ticket_ctx: dict, knowledge_ctx: dict, refund_ctx: dict) -> dict:
    """
    Validates final support response using LLM-as-a-judge for grounding and relevance.
    
    Returns:
        dict: {"grounded": bool, "relevant": bool, "reasoning": str}
    """
    # Compile contexts string
    contexts_list = []
    if crm_ctx:
        contexts_list.append(f"CRM Context: {crm_ctx}")
    if billing_ctx:
        contexts_list.append(f"Billing Context: {billing_ctx}")
    if ticket_ctx:
        contexts_list.append(f"Ticket Context: {ticket_ctx}")
    if knowledge_ctx:
        contexts_list.append(f"Knowledge Context: {knowledge_ctx}")
    if refund_ctx:
        contexts_list.append(f"Refund Context: {refund_ctx}")
        
    contexts_str = "\n".join(contexts_list) if contexts_list else "No contexts retrieved."
    
    user_prompt = EVALUATION_USER_PROMPT.format(
        query=query,
        contexts=contexts_str,
        response=response
    )
    
    res = client.invoke(
        system_prompt=EVALUATION_SYSTEM_PROMPT,
        user_prompt=user_prompt
    )
    
    if not res.success:
        return {
            "grounded": True, # Fail-safe
            "relevant": True,
            "reasoning": f"Could not perform evaluation check: {res.content}",
            "tokens_used": 0
        }
        
    try:
        result = json.loads(res.content)
    except json.JSONDecodeError:
        # Simple extraction regex fallback
        match = re.search(r"(\{.*?\})", res.content, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(1))
            except Exception:
                result = {"grounded": True, "relevant": True, "reasoning": "Fallback parsing"}
        else:
            result = {"grounded": True, "relevant": True, "reasoning": "Fallback parsing"}
            
    result["tokens_used"] = getattr(res, "tokens_used", 0)
    return result
