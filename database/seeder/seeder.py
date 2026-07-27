# pyrefly: ignore [missing-import]
from faker import Faker 
import pandas as pd
import random
import uuid
from datetime import datetime, timedelta

fake = Faker()

# CONFIG

NUM_ACCOUNTS = 50
NUM_INVOICES_PER_ACCOUNT = 12

PLANS = {
    "Starter": 29,
    "Growth": 99,
    "Business": 299,
    "Enterprise": 999
}

ACCOUNT_STATUSES = [
    "Active",
    "Past Due",
    "Suspended",
    "Trial"
]

USER_ROLES = [
    "owner",
    "admin",
    "member"
]

INVOICE_STATUSES = [
    "Paid",
    "Pending",
    "Overdue"
]

TICKET_STATUSES = [
    "Open",
    "In Progress",
    "Resolved",
    "Closed"
]

TICKET_PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

TICKET_SUBJECTS = [
    "Billing Issue",
    "Refund Request",
    "Cannot Login",
    "Invoice Dispute",
    "Subscription Upgrade",
    "Add Team Members",
    "API Error",
    "Workspace Access Problem",
    "Unexpected Charge",
    "Plan Downgrade Request"
]

LINE_ITEM_TYPES = [
    ("Subscription Plan", 1),
    ("Extra Storage", 50),
    ("Additional Users", 25),
    ("Priority Support", 100),
    ("API Usage", 10)
]

# DATA CONTAINERS

accounts = []
users = []
subscriptions = []
invoices = []
invoice_items = []
tickets = []

# ACCOUNT DISTRIBUTION

plan_distribution = (
    ["Starter"] * 20 +
    ["Growth"] * 15 +
    ["Business"] * 10 +
    ["Enterprise"] * 5
)

random.shuffle(plan_distribution)

# GENERATE DATA

for account_index in range(NUM_ACCOUNTS):

    account_id = str(uuid.uuid4())

    company_name = fake.company()

    plan = plan_distribution[account_index]

    monthly_price = PLANS[plan]

    account = {
        "id": account_id,
        "company_name": company_name,
        "plan_tier": plan,
        "account_status": random.choice(ACCOUNT_STATUSES),
        "contract_start": fake.date_between(
            start_date="-3y",
            end_date="-1y"
        ),
        "contract_end": fake.date_between(
            start_date="+30d",
            end_date="+2y"
        ),
        "seat_count": random.randint(5, 150),
        "monthly_revenue": monthly_price,
        "created_at": datetime.now()
    }

    accounts.append(account)

    # USERS

    num_users = random.randint(5, 10)

    owner_created = False

    for user_idx in range(num_users):

        if not owner_created:
            role = "owner"
            owner_created = True
        else:
            role = random.choice(["admin", "member"])

        name = fake.name()

        users.append({
            "id": str(uuid.uuid4()),
            "account_id": account_id,
            "full_name": name,
            "email": fake.unique.email(),
            "role": role,
            "created_at": datetime.now()
        })

    # SUBSCRIPTION

    subscriptions.append({
        "id": str(uuid.uuid4()),
        "account_id": account_id,
        "plan_name": plan,
        "billing_cycle": random.choice(
            ["Monthly", "Yearly"]
        ),
        "status": account["account_status"],
        "renewal_date": fake.date_between(
            start_date="+30d",
            end_date="+365d"
        ),
        "monthly_cost": monthly_price,
        "created_at": datetime.now()
    })

    # INVOICES

    for month in range(NUM_INVOICES_PER_ACCOUNT):

        invoice_id = str(uuid.uuid4())

        invoice_amount = monthly_price + random.randint(
            0,
            150
        )

        invoice_date = (
            datetime.now() -
            timedelta(days=30 * month)
        )

        invoices.append({
            "id": invoice_id,
            "account_id": account_id,
            "period": invoice_date.strftime("%Y-%m"),
            "amount": invoice_amount,
            "status": random.choice(INVOICE_STATUSES),
            "issued_date": invoice_date.date(),
            "created_at": datetime.now()
        })

        # INVOICE LINE ITEMS

        num_items = random.randint(3, 5)

        for _ in range(num_items):

            item_name, base_price = random.choice(
                LINE_ITEM_TYPES
            )

            invoice_items.append({
                "id": str(uuid.uuid4()),
                "invoice_id": invoice_id,
                "description": item_name,
                "amount": base_price + random.randint(
                    0,
                    100
                ),
                "usage_units": random.randint(
                    1,
                    500
                )
            })

    # TICKETS

    num_tickets = random.randint(5, 10)

    for _ in range(num_tickets):

        tickets.append({
            "id": str(uuid.uuid4()),
            "account_id": account_id,
            "subject": random.choice(
                TICKET_SUBJECTS
            ),
            "status": random.choice(
                TICKET_STATUSES
            ),
            "priority": random.choice(
                TICKET_PRIORITIES
            ),
            "summary": fake.paragraph(
                nb_sentences=3
            ),
            "created_at": fake.date_time_this_year()
        })

# DATAFRAMES

accounts_df = pd.DataFrame(accounts)
users_df = pd.DataFrame(users)
subscriptions_df = pd.DataFrame(subscriptions)
invoices_df = pd.DataFrame(invoices)
invoice_items_df = pd.DataFrame(invoice_items)
tickets_df = pd.DataFrame(tickets)

# SAVE CSV

accounts_df.to_csv(
    "accounts.csv",
    index=False
)

users_df.to_csv(
    "users.csv",
    index=False
)

subscriptions_df.to_csv(
    "subscriptions.csv",
    index=False
)

invoices_df.to_csv(
    "invoices.csv",
    index=False
)

invoice_items_df.to_csv(
    "invoice_line_items.csv",
    index=False
)

tickets_df.to_csv(
    "tickets.csv",
    index=False
)

# SUMMARY

print("\nDATASET GENERATED\n")

print("Accounts:", len(accounts_df))
print("Users:", len(users_df))
print("Subscriptions:", len(subscriptions_df))
print("Invoices:", len(invoices_df))
print("Invoice Items:", len(invoice_items_df))
print("Tickets:", len(tickets_df))