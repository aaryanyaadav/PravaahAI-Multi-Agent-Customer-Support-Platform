from database.connections import supabase


class AccountRepository:

    def get_account_by_id(
        self,
        account_id: str
    ):

        res = supabase.table("accounts").select("*").eq("id", account_id).execute()
        return res.data[0] if res.data else None

    def get_account_by_company_name(
        self,
        company_name: str
    ):

        res = supabase.table("accounts").select("*").eq("company_name", company_name).execute()
        return res.data[0] if res.data else None

    def list_accounts(
        self,
        limit: int = 20
    ):

        res = supabase.table("accounts").select("*").limit(limit).execute()
        return res.data