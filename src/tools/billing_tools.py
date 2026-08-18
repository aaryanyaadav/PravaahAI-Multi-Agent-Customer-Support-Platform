from collections import Counter
from datetime import datetime

from database.repositories.invoice_repository import (
    InvoiceRepository
)

from database.repositories.invoice_repository import (
    InvoiceLineItemRepository
)

invoice_repo = InvoiceRepository()

invoice_item_repo = (
    InvoiceLineItemRepository()
)
def get_invoice(
    invoice_id: str
):

    return (
        invoice_repo
        .get_invoice_by_id(
            invoice_id
        )
    )


def get_invoices(
    account_id: str
):

    return (
        invoice_repo
        .get_invoices_by_account(
            account_id
        )
    )


def get_latest_invoice(
    account_id: str
):

    return (
        invoice_repo
        .get_latest_invoice(
            account_id
        )
    )


def get_overdue_invoices(
    account_id: str
):

    return (
        invoice_repo
        .get_overdue_invoices(
            account_id
        )
    )

def get_invoice_items(
    invoice_id: str
):

    return (
        invoice_item_repo
        .get_items_by_invoice(
            invoice_id
        )
    )

def get_billing_summary(
    account_id: str
):

    invoices = (
        invoice_repo
        .get_invoices_by_account(
            account_id
        )
    )

    total_invoices = len(
        invoices
    )

    total_amount = sum(
        float(
            invoice["amount"]
        )
        for invoice in invoices
    )

    paid_count = len([
        invoice
        for invoice in invoices
        if invoice["status"]
        == "Paid"
    ])

    overdue_count = len([
        invoice
        for invoice in invoices
        if invoice["status"]
        == "Overdue"
    ])

    return {

        "total_invoices":
        total_invoices,

        "total_amount":
        round(total_amount, 2),

        "paid_invoices":
        paid_count,

        "overdue_invoices":
        overdue_count
    }

def get_payment_health(
    account_id: str
):

    invoices = (
        invoice_repo
        .get_invoices_by_account(
            account_id
        )
    )

    total = len(invoices)

    overdue = len([
        invoice
        for invoice in invoices
        if invoice["status"]
        == "Overdue"
    ])

    failed = len([
        invoice
        for invoice in invoices
        if invoice["status"]
        == "Failed"
    ])

    score = 100

    score -= overdue * 10

    score -= failed * 15

    score = max(
        score,
        0
    )

    if score >= 80:

        status = "Healthy"

    elif score >= 60:

        status = "Warning"

    else:

        status = "At Risk"

    return {

        "score": score,

        "status": status,

        "overdue_count":
        overdue,

        "failed_count":
        failed
    }

def explain_latest_charge(
    account_id: str
):

    invoice = (
        invoice_repo
        .get_latest_invoice(
            account_id
        )
    )

    if not invoice:

        return None

    items = (
        invoice_item_repo
        .get_items_by_invoice(
            invoice["id"]
        )
    )

    return {

        "invoice":
        invoice,

        "line_items":
        items,

        "total_amount":
        invoice["amount"]
    }

def get_payment_history(
    account_id: str
):

    invoices = (
        invoice_repo
        .get_invoices_by_account(
            account_id
        )
    )

    history = []

    for invoice in invoices:

        history.append({

            "invoice_id":
            invoice["id"],

            "amount":
            invoice["amount"],

            "status":
            invoice["status"],

            "issued_date":
            invoice["issued_date"]
        })

    return history

def get_invoice_status_breakdown(
    account_id: str
):

    invoices = (
        invoice_repo
        .get_invoices_by_account(
            account_id
        )
    )

    statuses = [

        invoice["status"]

        for invoice in invoices
    ]

    return dict(
        Counter(statuses)
    )

def get_total_spend(
    account_id: str
):

    invoices = (
        invoice_repo
        .get_invoices_by_account(
            account_id
        )
    )

    return round(

        sum(
            float(
                invoice["amount"]
            )
            for invoice in invoices
        ),

        2
    )

def check_refund_eligibility(
    invoice_id: str
):

    invoice = (
        invoice_repo
        .get_invoice_by_id(
            invoice_id
        )
    )

    if not invoice:

        return {

            "eligible": False,

            "reason":
            "Invoice not found"
        }

    if invoice["status"] != "Paid":

        return {

            "eligible": False,

            "reason":
            "Invoice not paid"
        }

    return {

        "eligible": True,

        "reason":
        "Invoice paid"
    }

def get_billing_risk(
    account_id: str
):

    health = (
        get_payment_health(
            account_id
        )
    )

    score = (
        health["score"]
    )

    if score >= 80:

        risk = "Low"

    elif score >= 60:

        risk = "Medium"

    else:

        risk = "High"

    return {

        "risk": risk,

        "score": score
    }
def get_highest_invoice(
    account_id: str
):

    invoices = (
        invoice_repo
        .get_invoices_by_account(
            account_id
        )
    )

    if not invoices:

        return None

    return max(

        invoices,

        key=lambda x:
        float(
            x["amount"]
        )
    )
def get_overdue_summary(
    account_id: str
):

    overdue = (
        invoice_repo
        .get_overdue_invoices(
            account_id
        )
    )

    amount = sum(

        float(
            invoice["amount"]
        )

        for invoice in overdue
    )

    return {

        "overdue_count":
        len(overdue),

        "overdue_amount":
        round(amount, 2)
    }