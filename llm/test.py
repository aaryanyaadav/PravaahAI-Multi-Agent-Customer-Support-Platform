from llm.groq_client import (
    GroqClient
)
client = GroqClient()
response = client.invoke(
    system_prompt="""
You are a CRM specialist.
""",
    user_prompt="""
What is a SaaS subscription?
"""
)
print(
    response.content
)