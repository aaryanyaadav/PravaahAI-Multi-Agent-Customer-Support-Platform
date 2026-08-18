from collections import Counter
from datetime import datetime

from database.repositories.ticket_repository import (
    TicketRepository
)

ticket_repo = TicketRepository()


# =====================================================
# BASIC TICKET OPERATIONS
# =====================================================

def get_ticket(ticket_id: str):

    return (
        ticket_repo
        .get_ticket_by_id(ticket_id)
    )


def get_account_tickets(account_id: str):

    return (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )


def get_open_tickets(account_id: str):

    return (
        ticket_repo
        .get_open_tickets(
            account_id
        )
    )


def create_ticket(
    account_id: str,
    subject: str,
    priority: str,
    summary: str
):

    return (
        ticket_repo
        .create_ticket(
            account_id=account_id,
            subject=subject,
            priority=priority,
            summary=summary
        )
    )


# =====================================================
# TICKET SEARCH
# =====================================================

def find_ticket_by_subject(
    account_id: str,
    keyword: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    return [

        ticket

        for ticket in tickets

        if keyword.lower()
        in ticket["subject"].lower()
    ]


def get_recent_tickets(
    account_id: str,
    limit: int = 5
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    return tickets[:limit]


# =====================================================
# TICKET ANALYTICS
# =====================================================

def get_ticket_summary(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    total = len(tickets)

    open_count = len([
        t
        for t in tickets
        if t["status"] == "Open"
    ])

    closed_count = len([
        t
        for t in tickets
        if t["status"] == "Closed"
    ])

    in_progress_count = len([
        t
        for t in tickets
        if t["status"] == "In Progress"
    ])

    return {

        "total_tickets": total,

        "open_tickets": open_count,

        "closed_tickets": closed_count,

        "in_progress_tickets":
        in_progress_count
    }


def get_unresolved_tickets(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    return [

        ticket

        for ticket in tickets

        if ticket["status"]
        != "Closed"
    ]


def get_closed_tickets(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    return [

        ticket

        for ticket in tickets

        if ticket["status"]
        == "Closed"
    ]


# =====================================================
# PRIORITY ANALYTICS
# =====================================================

def get_high_priority_tickets(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    return [

        ticket

        for ticket in tickets

        if ticket["priority"]
        in (
            "High",
            "Critical"
        )
    ]


def has_open_critical_ticket(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    critical = [

        ticket

        for ticket in tickets

        if (
            ticket["priority"]
            == "Critical"
            and
            ticket["status"]
            != "Closed"
        )
    ]

    return len(
        critical
    ) > 0


# =====================================================
# CATEGORY ANALYTICS
# =====================================================

def get_ticket_categories(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    categories = [

        ticket.get(
            "category",
            "Unknown"
        )

        for ticket in tickets
    ]

    return dict(
        Counter(categories)
    )


def get_most_common_issue(
    account_id: str
):

    categories = (
        get_ticket_categories(
            account_id
        )
    )

    if not categories:

        return None

    return max(
        categories,
        key=categories.get
    )


# =====================================================
# SLA / ACCOUNT HEALTH
# =====================================================

def get_ticket_health(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    total = len(tickets)

    open_tickets = len([
        t
        for t in tickets
        if t["status"]
        != "Closed"
    ])

    critical_open = len([
        t
        for t in tickets
        if (
            t["priority"]
            == "Critical"
            and
            t["status"]
            != "Closed"
        )
    ])

    if critical_open > 0:

        health = "Poor"

    elif open_tickets > 10:

        health = "Warning"

    else:

        health = "Healthy"

    return {

        "health": health,

        "total_tickets": total,

        "open_tickets": open_tickets,

        "critical_open":
        critical_open
    }


# =====================================================
# CUSTOMER SUPPORT INSIGHTS
# =====================================================

def get_customer_support_profile(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    total_tickets = len(tickets)

    open_tickets = len([
        t
        for t in tickets
        if t["status"]
        != "Closed"
    ])

    high_priority = len([
        t
        for t in tickets
        if t["priority"]
        in (
            "High",
            "Critical"
        )
    ])

    return {

        "total_tickets":
        total_tickets,

        "open_tickets":
        open_tickets,

        "high_priority_tickets":
        high_priority,

        "most_common_issue":
        get_most_common_issue(
            account_id
        ),

        "health":
        get_ticket_health(
            account_id
        )["health"]
    }


# =====================================================
# ESCALATION HELPERS
# =====================================================

def needs_escalation(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    critical_open = [

        t

        for t in tickets

        if (
            t["priority"]
            == "Critical"
            and
            t["status"]
            != "Closed"
        )
    ]

    return len(
        critical_open
    ) > 0


def get_escalation_candidates(
    account_id: str
):

    tickets = (
        ticket_repo
        .get_tickets_by_account(
            account_id
        )
    )

    return [

        ticket

        for ticket in tickets

        if (
            ticket["priority"]
            in (
                "High",
                "Critical"
            )
            and
            ticket["status"]
            != "Closed"
        )
    ]