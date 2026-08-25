from src.agents.base.base_agent import BaseAgent
from src.agents.ticket.ticket_prompt import TICKET_SYSTEM_PROMPT


class TicketAgent(BaseAgent):
    """
    Ticket Domain Expert

    Responsibilities:
    - Ticket Lookup
    - Ticket Status Analysis
    - Ticket Investigation
    - Open Ticket Review
    - Ticket Health Analysis
    - Support Activity Summary
    """

    def __init__(self):

        super().__init__(
            domain="ticket",
            system_prompt=TICKET_SYSTEM_PROMPT
        )