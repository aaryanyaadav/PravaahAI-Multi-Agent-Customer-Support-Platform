# agents/ticket/test_ticket.py

from ticket_agent import (
    TicketAgent
)

agent = TicketAgent()

# Query tickets of account 8c1d9bef-0ab1-4233-a643-0a32d8fb95d4
response = agent.invoke(
    "How many open tickets does account 8c1d9bef-0ab1-4233-a643-0a32d8fb95d4 have?"
)

print(response)
