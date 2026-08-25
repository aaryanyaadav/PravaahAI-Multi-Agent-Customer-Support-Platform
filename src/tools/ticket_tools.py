from database.repositories.ticket_repository import TicketRepository

ticket_repo = TicketRepository()

def get_ticket(ticket_id: str):
    return ticket_repo.get_ticket_by_id(ticket_id)

def get_tickets(account_id: str):
    return ticket_repo.get_tickets_by_account(account_id)

def get_open_tickets(account_id: str):
    return ticket_repo.get_open_tickets(account_id)

def create_ticket(account_id: str, subject: str, priority: str, summary: str):
    return ticket_repo.create_ticket(account_id, subject, priority, summary)

def update_ticket_status(ticket_id: str, status: str, escalation_reason: str = None):
    return ticket_repo.update_ticket_status(ticket_id, status, escalation_reason)

def assign_queue(ticket_id: str, queue: str):
    return ticket_repo.assign_queue(ticket_id, queue)
