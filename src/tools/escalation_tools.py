from database.repositories.ticket_repository import TicketRepository

ticket_repo = TicketRepository()

def escalate_ticket(ticket_id: str, reason: str):
    return ticket_repo.update_ticket_status(ticket_id, "Escalated", escalation_reason=reason)

def assign_l2_queue(ticket_id: str, queue_name: str = "L2_Support"):
    return ticket_repo.assign_queue(ticket_id, queue_name)
