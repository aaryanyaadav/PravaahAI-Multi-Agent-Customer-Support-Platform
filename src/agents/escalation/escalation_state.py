from typing import TypedDict


class EscalationState(TypedDict):

    query: str

    source_agent: str

    failure_reason: str

    escalation_summary: str

    ticket_id: str