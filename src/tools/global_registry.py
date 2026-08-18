from src.tools.registry import ToolRegistry
from src.tools.definitions import ToolDefinition

tool_registry = ToolRegistry()

# Import CRM tools
import src.tools.crm_tools as crm_tools
# Import Billing tools
import src.tools.billing_tools as billing_tools
# Import Ticket tools
import src.tools.ticket_tools as ticket_tools
# Import Escalation tools
import src.tools.escalation_tools as escalation_tools
# Import Knowledge tools
import src.tools.knowledge_tools as knowledge_tools

# Register CRM tools
crm_functions = [
    ("get_account", "Get account by ID.", crm_tools.get_account),
    ("get_account_by_company", "Get account by company.", crm_tools.get_account_by_company),
    ("list_accounts", "List all accounts.", crm_tools.list_accounts),
    ("get_users", "Get account users.", crm_tools.get_users),
    ("get_active_users", "Get active users.", crm_tools.get_active_users),
    ("get_admin_users", "Get admin/owner users.", crm_tools.get_admin_users),
    ("get_subscription", "Get subscription.", crm_tools.get_subscription),
    ("get_contract_status", "Get contract status.", crm_tools.get_contract_status),
    ("get_seat_utilization", "Get seat utilization.", crm_tools.get_seat_utilization),
    ("get_customer_profile", "Get full customer profile.", crm_tools.get_customer_profile),
    ("get_account_health", "Get account health.", crm_tools.get_account_health),
    ("recommend_plan_upgrade", "Recommend plan upgrade.", crm_tools.recommend_plan_upgrade),
    ("get_churn_risk", "Get churn risk.", crm_tools.get_churn_risk),
]

for name, desc, func in crm_functions:
    tool_registry.register(ToolDefinition(name=name, description=desc, domain="crm", function=func))

# Register Billing tools
billing_functions = [
    ("get_invoice", "Get invoice by ID.", billing_tools.get_invoice),
    ("get_invoices", "Get all invoices.", billing_tools.get_invoices),
    ("get_latest_invoice", "Get latest invoice.", billing_tools.get_latest_invoice),
    ("get_overdue_invoices", "Get overdue invoices.", billing_tools.get_overdue_invoices),
    ("get_invoice_items", "Get invoice line items.", billing_tools.get_invoice_items),
    ("get_billing_summary", "Get billing summary.", billing_tools.get_billing_summary),
    ("get_payment_health", "Get payment health.", billing_tools.get_payment_health),
    ("explain_latest_charge", "Explain latest charge.", billing_tools.explain_latest_charge),
    ("get_payment_history", "Get payment history.", billing_tools.get_payment_history),
    ("get_invoice_status_breakdown", "Get invoice status breakdown.", billing_tools.get_invoice_status_breakdown),
    ("get_total_spend", "Get total spent.", billing_tools.get_total_spend),
    ("check_refund_eligibility", "Check refund eligibility.", billing_tools.check_refund_eligibility),
    ("get_billing_risk", "Get billing risk.", billing_tools.get_billing_risk),
    ("get_highest_invoice", "Get highest invoice.", billing_tools.get_highest_invoice),
    ("get_overdue_summary", "Get overdue summary.", billing_tools.get_overdue_summary),
]

for name, desc, func in billing_functions:
    tool_registry.register(ToolDefinition(name=name, description=desc, domain="billing", function=func))

# Register Refund tools
refund_functions = [
    ("check_refund_eligibility", "Check refund eligibility.", billing_tools.check_refund_eligibility),
]

for name, desc, func in refund_functions:
    tool_registry.register(ToolDefinition(name=name, description=desc, domain="refund", function=func))

# Register Ticket tools
ticket_functions = [
    ("get_ticket", "Get ticket details.", ticket_tools.get_ticket),
    ("get_account_tickets", "Get all account tickets.", ticket_tools.get_account_tickets),
    ("get_open_tickets", "Get open tickets.", ticket_tools.get_open_tickets),
    ("create_ticket", "Create support ticket.", ticket_tools.create_ticket),
    ("find_ticket_by_subject", "Find ticket by subject keyword.", ticket_tools.find_ticket_by_subject),
    ("get_recent_tickets", "Get recent tickets.", ticket_tools.get_recent_tickets),
    ("get_ticket_summary", "Get ticket summary.", ticket_tools.get_ticket_summary),
    ("get_unresolved_tickets", "Get unresolved tickets.", ticket_tools.get_unresolved_tickets),
    ("get_closed_tickets", "Get closed tickets.", ticket_tools.get_closed_tickets),
    ("get_high_priority_tickets", "Get high priority tickets.", ticket_tools.get_high_priority_tickets),
    ("has_open_critical_ticket", "Check open critical ticket.", ticket_tools.has_open_critical_ticket),
    ("get_ticket_categories", "Get ticket categories count.", ticket_tools.get_ticket_categories),
    ("get_most_common_issue", "Get most common issue.", ticket_tools.get_most_common_issue),
    ("get_ticket_health", "Get ticket health.", ticket_tools.get_ticket_health),
    ("get_customer_support_profile", "Get customer support profile.", ticket_tools.get_customer_support_profile),
    ("needs_escalation", "Check if needs escalation.", ticket_tools.needs_escalation),
    ("get_escalation_candidates", "Get escalation candidates.", ticket_tools.get_escalation_candidates),
]

for name, desc, func in ticket_functions:
    tool_registry.register(ToolDefinition(name=name, description=desc, domain="ticket", function=func))

# Register Escalation tools
escalation_functions = [
    ("create_escalation", "Create ticket escalation.", escalation_tools.create_escalation),
    ("mark_ticket_escalated", "Mark ticket escalated.", escalation_tools.mark_ticket_escalated),
    ("assign_human_queue", "Assign ticket to human queue.", escalation_tools.assign_human_queue),
    ("generate_escalation_summary", "Generate escalation summary.", escalation_tools.generate_escalation_summary),
]

for name, desc, func in escalation_functions:
    tool_registry.register(ToolDefinition(name=name, description=desc, domain="escalation", function=func))

# Register Knowledge tools
knowledge_functions = [
    ("retrieve_faq", "Get FAQ details.", knowledge_tools.retrieve_faq),
    ("retrieve_policy", "Get policy details.", knowledge_tools.retrieve_policy),
]

for name, desc, func in knowledge_functions:
    tool_registry.register(ToolDefinition(name=name, description=desc, domain="knowledge", function=func))