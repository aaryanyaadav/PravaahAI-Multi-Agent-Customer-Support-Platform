from pydantic import BaseModel
from typing import Optional


class TicketContext(BaseModel):

    ticket_id: Optional[str] = None

    ticket_status: Optional[str] = None

    priority: Optional[str] = None

    subject: Optional[str] = None

    open_ticket_count: int = 0