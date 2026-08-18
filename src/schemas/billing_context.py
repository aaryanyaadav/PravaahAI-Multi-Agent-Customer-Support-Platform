from pydantic import BaseModel
from typing import Optional


class BillingContext(BaseModel):

    invoice_id: Optional[str] = None

    invoice_amount: Optional[float] = None

    invoice_status: Optional[str] = None

    billing_period: Optional[str] = None

    overdue_invoices: int = 0

    latest_payment_status: Optional[str] = None