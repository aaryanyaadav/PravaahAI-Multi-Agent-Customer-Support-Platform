from database.repositories.ticket_repository import (
    TicketRepository
)

ticket_repo = TicketRepository()

def create_escalation(
    ticket_id: str,
    reason: str = None,
    **kwargs
):
    actual_reason = reason or kwargs.get("escalation_reason") or kwargs.get("reason") or "No reason provided"
    return ticket_repo.update_ticket_status(
        ticket_id=ticket_id,
        status="Escalated",
        escalation_reason=actual_reason
    )

def mark_ticket_escalated(
    ticket_id: str,
    **kwargs
):
    return ticket_repo.update_ticket_status(
        ticket_id=ticket_id,
        status="Escalated"
    )

def assign_human_queue(
    ticket_id: str,
    queue: str = None,
    **kwargs
):
    actual_queue = queue or kwargs.get("queue") or kwargs.get("reason") or "L2 Support"
    return ticket_repo.assign_queue(
        ticket_id=ticket_id,
        queue=actual_queue
    )

def generate_escalation_summary(
    ticket_id: str,
    ai_summary: str = None,
    **kwargs
):
    actual_summary = ai_summary or kwargs.get("ai_summary") or kwargs.get("reason") or kwargs.get("summary") or "No summary provided"
    return {
        "ticket_id": ticket_id,
        "summary": actual_summary,
        "status": "Escalated"
    }
