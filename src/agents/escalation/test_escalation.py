from escalation_agent import (
    EscalationAgent
)

agent = EscalationAgent()

# Escalation query for ticket f4996a7b-e9f3-483d-840c-f1e42d293c20
response = agent.invoke(
    "Please escalate ticket f4996a7b-e9f3-483d-840c-f1e42d293c20 because the customer is unhappy with the service."
)

print(response)
