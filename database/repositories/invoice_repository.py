from database.connections import supabase
class InvoiceRepository:
    def get_invoice_by_id(
        self,
        invoice_id: str
    ):
        res = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        return res.data[0] if res.data else None
    def get_invoices_by_account(
        self,
        account_id: str
    ):
        res = supabase.table("invoices").select("*").eq("account_id", account_id).order("issued_date", desc=True).execute()
        return res.data
    def get_latest_invoice(
        self,
        account_id: str
    ):
        res = supabase.table("invoices").select("*").eq("account_id", account_id).order("issued_date", desc=True).limit(1).execute()
        return res.data[0] if res.data else None
    def get_overdue_invoices(
        self,
        account_id: str
    ):

        res = supabase.table("invoices").select("*").eq("account_id", account_id).eq("status", "Overdue").execute()
        return res.data
class InvoiceLineItemRepository:

    def get_items_by_invoice(
        self,
        invoice_id: str
    ):

        res = supabase.table("invoice_line_items").select("*").eq("invoice_id", invoice_id).execute()
        return res.data