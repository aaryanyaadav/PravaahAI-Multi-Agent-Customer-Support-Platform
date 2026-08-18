# guardrails/input_guard.py

import re

# Regex patterns for PII
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

# Dangerous keywords indicative of prompt injection attempts
INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "bypass system prompt",
    "ignore instructions",
    "dan mode",
    "you are now an",
    "you are now a",
    "ignore all instructions",
    "system override",
    "bypass instructions",
    "ignore rules",
    "forget previous instructions"
]

# Abusive keywords
ABUSIVE_KEYWORDS = [
    "stupid bot", "useless bot", "idiot", "bastard", "bitch", "shut up",
    "fuck", "asshole", "dumb bot", "motherfucker", "crap bot"
]

def redact_pii(text: str) -> str:
    """Redacts Credit Card Numbers, SSNs, and Emails with [REDACTED]."""
    text = CREDIT_CARD_REGEX.sub("[REDACTED_CARD]", text)
    text = SSN_REGEX.sub("[REDACTED_SSN]", text)
    text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    return text

def validate_input(query: str) -> dict:
    """
    Validates user query for prompt injection and toxic/abusive text.
    Redacts PII details.
    
    Returns:
        dict: {"safe": bool, "query": str, "reason": str}
    """
    cleaned_query = query.strip()
    query_lower = cleaned_query.lower()
    
    # 1. Check prompt injection
    for keyword in INJECTION_KEYWORDS:
        if keyword in query_lower:
            return {
                "safe": False,
                "query": cleaned_query,
                "reason": "Prompt injection attempt detected."
            }
            
    # 2. Check toxic/abuse content
    for keyword in ABUSIVE_KEYWORDS:
        if keyword in query_lower:
            return {
                "safe": False,
                "query": cleaned_query,
                "reason": "Abusive or offensive language detected."
            }
            
    # 3. Redact PII
    redacted_query = redact_pii(cleaned_query)
    
    return {
        "safe": True,
        "query": redacted_query,
        "reason": "Input checks passed successfully."
    }
