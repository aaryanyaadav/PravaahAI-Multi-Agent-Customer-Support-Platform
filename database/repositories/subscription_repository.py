from database.connections import supabase
class SubscriptionRepository:

    def get_subscription(
        self,
        account_id: str
    ):
        res = supabase.table("subscriptions").select("*").eq("account_id", account_id).execute()
        return res.data[0] if res.data else None