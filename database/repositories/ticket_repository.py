from datetime import datetime
import uuid
from database.connections import supabase
class TicketRepository:

    def get_ticket_by_id(
        self,
        ticket_id: str
    ):

        res = supabase.table("tickets").select("*").eq("id", ticket_id).execute()
        return res.data[0] if res.data else None

    def get_tickets_by_account(
        self,
        account_id: str
    ):

        res = supabase.table("tickets").select("*").eq("account_id", account_id).order("created_at", desc=True).execute()
        return res.data

    def get_open_tickets(
        self,
        account_id: str
    ):

        res = supabase.table("tickets").select("*").eq("account_id", account_id).eq("status", "Open").order("created_at", desc=True).execute()
        return res.data


    def create_ticket(
        self,
        account_id: str,
        subject: str,
        priority: str,
        summary: str
    ):
        ticket_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        row = {
            "id": ticket_id,
            "account_id": account_id,
            "subject": subject,
            "priority": priority,
            "summary": summary,
            "status": "Open",
            "created_at": created_at
        }

        res = supabase.table("tickets").insert(row).execute()
        return res.data[0] if res.data else None

    def update_ticket_status(
        self,
        ticket_id: str,
        status: str,
        escalation_reason: str = None
    ):

        update_data = {"status": status}
        if escalation_reason is not None:
            ticket = self.get_ticket_by_id(ticket_id)
            if ticket:
                current_summary = ticket.get("summary") or ""
                update_data["summary"] = f"{current_summary}\n[Escalation Reason]: {escalation_reason}".strip()

        res = supabase.table("tickets").update(update_data).eq("id", ticket_id).execute()
        return res.data[0] if res.data else None

    def assign_queue(
        self,
        ticket_id: str,
        queue: str
    ):

        res = supabase.table("tickets").update({"queue": queue}).eq("id", ticket_id).execute()
        return res.data[0] if res.data else None