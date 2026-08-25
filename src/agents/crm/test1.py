from crm_agent import (
    CRMAgent
)

agent = CRMAgent()

response = agent.invoke(
    "What is the health of account 0e58b9cb-4212-482b-b666-cda251da4553 ?"
)

print(response)