from src.tools.registry import ToolRegistry
from src.tools.crm_tools import (
    get_account, get_account_by_company, list_accounts,
    get_users, get_active_users, get_admin_users,
    get_subscription, get_contract_status, get_seat_utilization,
    get_customer_profile, get_account_health, recommend_plan_upgrade,
    get_churn_risk
)
from src.tools.billing_tools import (
    get_invoice, get_invoices, get_latest_invoice, get_overdue_invoices,
    get_invoice_items, get_billing_summary, get_payment_health,
    explain_latest_charge, get_payment_history, get_invoice_status_breakdown,
    get_total_spend, check_refund_eligibility, get_billing_risk,
    get_highest_invoice, get_overdue_summary
)
from src.tools.knowledge_tools import (
    retrieve_faq, retrieve_policy
)
from src.tools.ticket_tools import (
    get_ticket, get_tickets, get_open_tickets, create_ticket,
    update_ticket_status, assign_queue
)
from src.tools.escalation_tools import (
    escalate_ticket, assign_l2_queue
)

tool_registry = ToolRegistry()

# CRM tools
tool_registry.register("get_account", "Get account details by ID", "crm", get_account)
tool_registry.register("get_account_by_company", "Get account details by company name", "crm", get_account_by_company)
tool_registry.register("list_accounts", "List accounts in database", "crm", list_accounts)
tool_registry.register("get_users", "Get all users belonging to an account", "crm", get_users)
tool_registry.register("get_active_users", "Get active users for an account", "crm", get_active_users)
tool_registry.register("get_admin_users", "Get admin and owner users for an account", "crm", get_admin_users)
tool_registry.register("get_subscription", "Get subscription details for an account", "crm", get_subscription)
tool_registry.register("get_contract_status", "Get contract end date and remaining days", "crm", get_contract_status)
tool_registry.register("get_seat_utilization", "Get seat utilization metrics", "crm", get_seat_utilization)
tool_registry.register("get_customer_profile", "Get complete customer profile (account, users, subscription)", "crm", get_customer_profile)
tool_registry.register("get_account_health", "Calculate account health score", "crm", get_account_health)
tool_registry.register("recommend_plan_upgrade", "Analyze if account needs plan upgrade", "crm", recommend_plan_upgrade)
tool_registry.register("get_churn_risk", "Assess churn risk for account", "crm", get_churn_risk)

# Billing tools
tool_registry.register("get_invoice", "Get single invoice details by invoice ID", "billing", get_invoice)
tool_registry.register("get_invoices", "Get all invoices for an account", "billing", get_invoices)
tool_registry.register("get_latest_invoice", "Get the most recent invoice for an account", "billing", get_latest_invoice)
tool_registry.register("get_overdue_invoices", "Get overdue invoices for an account", "billing", get_overdue_invoices)
tool_registry.register("get_invoice_items", "Get line items for a specific invoice", "billing", get_invoice_items)
tool_registry.register("get_billing_summary", "Get overall billing summary for an account", "billing", get_billing_summary)
tool_registry.register("get_payment_health", "Calculate payment health score and overdue/failed count", "billing", get_payment_health)
tool_registry.register("explain_latest_charge", "Breakdown and explain latest invoice charges and line items", "billing", explain_latest_charge)
tool_registry.register("get_payment_history", "Get payment history list", "billing", get_payment_history)
tool_registry.register("get_invoice_status_breakdown", "Get counts of invoices grouped by status", "billing", get_invoice_status_breakdown)
tool_registry.register("get_total_spend", "Calculate total spend across all invoices", "billing", get_total_spend)
tool_registry.register("check_refund_eligibility", "Check if invoice is eligible for refund", "billing", check_refund_eligibility)
tool_registry.register("get_billing_risk", "Get billing risk assessment", "billing", get_billing_risk)
tool_registry.register("get_highest_invoice", "Get the highest amount invoice for an account", "billing", get_highest_invoice)
tool_registry.register("get_overdue_summary", "Get count and total amount of overdue invoices", "billing", get_overdue_summary)

# Knowledge tools
tool_registry.register("retrieve_faq", "Search FAQ knowledge base using semantic/BM25 retrieval", "knowledge", retrieve_faq)
tool_registry.register("retrieve_policy", "Search policy knowledge base using semantic/BM25 retrieval", "knowledge", retrieve_policy)

# Ticket tools
tool_registry.register("get_ticket", "Get ticket by ticket ID", "ticket", get_ticket)
tool_registry.register("get_tickets", "Get all tickets for an account", "ticket", get_tickets)
tool_registry.register("get_open_tickets", "Get currently open tickets for an account", "ticket", get_open_tickets)
tool_registry.register("create_ticket", "Create a new support ticket in database", "ticket", create_ticket)
tool_registry.register("update_ticket_status", "Update ticket status or add escalation reason", "ticket", update_ticket_status)
tool_registry.register("assign_queue", "Assign ticket to a support queue", "ticket", assign_queue)

# Refund tools
tool_registry.register("check_refund_eligibility", "Check if invoice is eligible for refund", "refund", check_refund_eligibility)
tool_registry.register("get_invoices", "Get all invoices for an account", "refund", get_invoices)
tool_registry.register("get_latest_invoice", "Get latest invoice", "refund", get_latest_invoice)
tool_registry.register("retrieve_policy", "Search refund policy rules", "refund", retrieve_policy)

# Escalation tools
tool_registry.register("escalate_ticket", "Escalate ticket to human support", "escalation", escalate_ticket)
tool_registry.register("assign_l2_queue", "Assign ticket to L2 queue", "escalation", assign_l2_queue)
tool_registry.register("create_ticket", "Create escalated ticket", "escalation", create_ticket)
