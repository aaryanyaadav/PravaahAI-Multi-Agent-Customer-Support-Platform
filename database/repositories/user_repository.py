from database.connections import supabase
class UserRepository:

    def get_user_by_email(
        self,
        email: str
    ):
        res = supabase.table("users").select("*").eq("email", email).execute()
        if res.data:
            user = res.data[0]
            if "status" not in user or user["status"] is None:
                user["status"] = "Active"
            return user
        return None

    def get_users_by_account(
        self,
        account_id: str
    ):

        res = supabase.table("users").select("*").eq("account_id", account_id).execute()
        users = res.data
        for user in users:
            if "status" not in user or user["status"] is None:
                user["status"] = "Active"
        return users