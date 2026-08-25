from pydantic import BaseModel
from typing import Optional


class CustomerContext(BaseModel):

    account_id: str

    company_name: str

    account_status: str

    plan_tier: str

    seat_count: int

    monthly_revenue: float

    primary_contact: Optional[str] = None

    primary_email: Optional[str] = None