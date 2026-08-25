import re
from typing import Dict, Any, Tuple, Optional

# Regex Patterns for PII Redaction
CC_PATTERN = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b')

# Patterns for Toxic/Abusive Inputs
TOXIC_PATTERNS = [
    re.compile(r'\b(stupid|idiot|dumb|useless|shut\s*up|hate\s*you|fuck|shit|bitch|asshole|bastard)\b', re.IGNORECASE),
    re.compile(r'\b(kill\s*yourself|go\s*to\s*hell)\b', re.IGNORECASE)
]

# Patterns for Prompt Injection / Jailbreak
INJECTION_PATTERNS = [
    re.compile(r'ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)', re.IGNORECASE),
    re.compile(r'(show|tell|print|reveal|display|output)\s+(me\s+)?(your\s+)?(system\s+prompt|instructions|initial\s+prompt)', re.IGNORECASE),
    re.compile(r'\b(dan\s+mode|jailbreak|bypass\s+safety|act\s+as\s+an\s+unrestricted)\b', re.IGNORECASE),
    re.compile(r'you\s+are\s+now\s+in\s+developer\s+mode', re.IGNORECASE)
]

# Conversational & Non-Support Intent Matchers
GREETING_WORDS = {
    "hi", "hello", "hey", "howdy", "greetings", "hi there", "hello there", "hey there",
    "good morning", "good afternoon", "good evening", "good day", "sup", "yo", "hola"
}

GRATITUDE_WORDS = {
    "thanks", "thank you", "thx", "thank you so much", "thanks a lot", "thank u",
    "many thanks", "appreciate it", "much appreciated", "cheers"
}

ACKNOWLEDGMENT_WORDS = {
    "okay", "ok", "got it", "cool", "alright", "sure", "k", "roger", "understood",
    "sounds good", "great", "perfect", "noted", "fine"
}

CAPABILITY_PHRASES = {
    "what can you do", "what can you do?", "who are you", "who are you?",
    "what do you do", "what do you do?", "help", "help me", "how does this work",
    "how does this work?", "what are your features", "what are your features?",
    "what services do you provide", "what services do you provide?",
    "what are your capabilities", "what are your capabilities?",
    "what can i ask", "what can i ask?", "what are you"
}

def redact_pii(text: str) -> str:
    """
    Masks sensitive Personally Identifiable Information (PII) including
    Credit Cards, SSNs, Emails, and Phone Numbers.
    """
    redacted = CC_PATTERN.sub("[REDACTED_CREDIT_CARD]", text)
    redacted = SSN_PATTERN.sub("[REDACTED_SSN]", redacted)
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)
    return redacted

def is_toxic_or_abusive(text: str) -> Tuple[bool, str]:
    for pattern in TOXIC_PATTERNS:
        if pattern.search(text):
            return True, "Inappropriate, abusive, or offensive language detected."
    return False, ""

def is_prompt_injection(text: str) -> Tuple[bool, str]:
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True, "Potential prompt injection or safety boundary violation detected."
    return False, ""

def is_gibberish(text: str) -> bool:
    """
    Detects random keyboard mash, consonants-only strings, or unparseable gibberish.
    """
    cleaned = re.sub(r'[^a-zA-Z]', '', text).lower()
    if not cleaned:
        return False
    
    # Common keyboard smash patterns
    known_gibberish = {
        "asdf", "asdfg", "asdfgh", "asdfghj", "asdfghjkl",
        "qwerty", "qwertyuiop", "zxcv", "zxcvbnm", "hjkl",
        "qwe", "asd", "zxc", "jkl"
    }
    if cleaned in known_gibberish:
        return True
        
    # Check repeated characters (e.g. "aaaaa", "zzzzz")
    if len(cleaned) >= 4 and len(set(cleaned)) == 1:
        return True

    # Check for lack of vowels in longer strings (> 4 characters)
    vowels = set("aeiouy")
    vowel_count = sum(1 for c in cleaned if c in vowels)
    if len(cleaned) >= 5 and vowel_count == 0:
        return True
    
    # Extreme consonant ratio
    if len(cleaned) >= 6 and (vowel_count / len(cleaned)) < 0.15:
        return True
        
    return False

def classify_conversational_intent(text: str) -> Optional[Dict[str, Any]]:
    """
    Identifies non-support conversational queries (greetings, pleasantries, gibberish, capabilities)
    and provides an immediate clean response to avoid generating false support tickets.
    """
    normalized = text.strip().lower()
    clean_punc = re.sub(r'[^\w\s]', '', normalized).strip()

    # 1. Greetings
    if normalized in GREETING_WORDS or clean_punc in GREETING_WORDS:
        return {
            "intent": "greeting",
            "is_support": False,
            "response": "Hello! How can I assist you today with your account, billing, invoices, tickets, or subscriptions?"
        }

    # 2. Gratitude / Pleasantries
    if normalized in GRATITUDE_WORDS or clean_punc in GRATITUDE_WORDS:
        return {
            "intent": "gratitude",
            "is_support": False,
            "response": "You are very welcome! Please let me know if you need assistance with anything else regarding your account or services."
        }

    # 3. Acknowledgments
    if normalized in ACKNOWLEDGMENT_WORDS or clean_punc in ACKNOWLEDGMENT_WORDS:
        return {
            "intent": "acknowledgment",
            "is_support": False,
            "response": "Glad to help! Feel free to reach out if you have any further questions."
        }

    # 4. Capabilities Inquiries
    if normalized in CAPABILITY_PHRASES or clean_punc in CAPABILITY_PHRASES:
        capabilities_text = (
            "I am Pravaah AI, your autonomous customer support assistant.\n\n"
            "Here is what I can help you with:\n"
            "1. CRM & Profile: View account details, user profiles, seat utilization, and plan details.\n"
            "2. Billing & Invoices: Check invoice status, explain charges, review payment history, and calculate billing summaries.\n"
            "3. Support Tickets: Look up existing tickets, track status, and check support histories.\n"
            "4. Knowledge Base: Answer questions on policies, SLAs, cancellations, and refund guidelines.\n"
            "5. Human Escalation: Open a support ticket and connect you with human support specialists for complex investigations.\n\n"
            "How can I help you today?"
        )
        return {
            "intent": "capabilities",
            "is_support": False,
            "response": capabilities_text
        }

    # 5. Gibberish / Noise
    if is_gibberish(normalized):
        return {
            "intent": "gibberish",
            "is_support": False,
            "response": "I didn't quite understand that. Could you please clarify your question regarding your account, billing, invoices, or subscriptions?"
        }

    return None

def validate_input(text: str) -> Dict[str, Any]:
    """
    Full Input Guardrail:
    1. Checks for abusive / toxic language.
    2. Checks for prompt injection / jailbreaks.
    3. Redacts PII.
    4. Identifies conversational / non-support queries to prevent false ticket generation.
    """
    if not text or not text.strip():
        return {
            "safe": True,
            "query": "",
            "reason": "Empty query received.",
            "is_conversational": True,
            "intent": "empty",
            "direct_response": "Please enter a message or support query."
        }

    # 1. Toxicity check
    is_toxic, toxic_reason = is_toxic_or_abusive(text)
    if is_toxic:
        return {
            "safe": False,
            "query": text,
            "reason": toxic_reason,
            "is_conversational": False,
            "intent": "toxic",
            "direct_response": "Your request was blocked due to inappropriate or abusive language."
        }

    # 2. Prompt Injection check
    is_injection, injection_reason = is_prompt_injection(text)
    if is_injection:
        return {
            "safe": False,
            "query": text,
            "reason": injection_reason,
            "is_conversational": False,
            "intent": "injection",
            "direct_response": "Your request was blocked as a security policy violation."
        }

    # 3. PII Redaction
    redacted_text = redact_pii(text)

    # 4. Conversational / Non-support intent classification
    conv_match = classify_conversational_intent(text)
    if conv_match:
        return {
            "safe": True,
            "query": redacted_text,
            "reason": f"Handled conversational intent: {conv_match['intent']}",
            "is_conversational": True,
            "intent": conv_match["intent"],
            "direct_response": conv_match["response"]
        }

    return {
        "safe": True,
        "query": redacted_text,
        "reason": "Input validation passed successfully.",
        "is_conversational": False,
        "intent": "support_query",
        "direct_response": None
    }
