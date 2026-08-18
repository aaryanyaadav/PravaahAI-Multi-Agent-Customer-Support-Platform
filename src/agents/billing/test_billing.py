from billing_agent import (
    BillingAgent
)

agent = BillingAgent()

# Query total spend of account 8c1d9bef-0ab1-4233-a643-0a32d8fb95d4
response = agent.invoke(
    "What is the total spent by account 8c1d9bef-0ab1-4233-a643-0a32d8fb95d4 ?"
)

print(response)
