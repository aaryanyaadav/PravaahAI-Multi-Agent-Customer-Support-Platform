from pydantic import BaseModel
from typing import Optional


class SubscriptionContext(BaseModel):

    subscription_id: Optional[str] = None

    plan_name: Optional[str] = None

    billing_cycle: Optional[str] = None

    status: Optional[str] = None

    renewal_date: Optional[str] = None