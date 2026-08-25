# agents/knowledge/test_knowledge.py

from knowledge_agent import (
    KnowledgeAgent
)

agent = KnowledgeAgent()

# Query FAQ
response_faq = agent.invoke(
    "How do I create an account?"
)
print("=== FAQ Query Response ===")
print(response_faq)
print()

# Query Policy
response_policy = agent.invoke(
    "What is the refund policy?"
)
print("=== Policy Query Response ===")
print(response_policy)
