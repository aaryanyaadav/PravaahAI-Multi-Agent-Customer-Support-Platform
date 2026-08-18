from datetime import datetime

from database.repositories.account_repository import (
    AccountRepository
)

from database.repositories.user_repository import (
    UserRepository
)

from database.repositories.subscription_repository import (
    SubscriptionRepository
)

account_repo = AccountRepository()
user_repo = UserRepository()
subscription_repo = SubscriptionRepository()

def get_account(
    account_id: str
):

    return (
        account_repo
        .get_account_by_id(
            account_id
        )
    )


def get_account_by_company(
    company_name: str
):

    return (
        account_repo
        .get_account_by_company_name(
            company_name
        )
    )


def list_accounts():

    return (
        account_repo
        .list_accounts(
            limit=100
        )
    )

def get_users(
    account_id: str
):

    return (
        user_repo
        .get_users_by_account(
            account_id
        )
    )


def get_active_users(
    account_id: str
):

    users = (
        user_repo
        .get_users_by_account(
            account_id
        )
    )

    return [

        user

        for user in users

        if user["status"]
        == "Active"
    ]


def get_admin_users(
    account_id: str
):

    users = (
        user_repo
        .get_users_by_account(
            account_id
        )
    )

    return [

        user

        for user in users

        if user["role"]
        in (
            "Admin",
            "Owner"
        )
    ]
def get_subscription(
    account_id: str
):

    return (
        subscription_repo
        .get_subscription(
            account_id
        )
    )

def get_contract_status(
    account_id: str
):

    account = (
        account_repo
        .get_account_by_id(
            account_id
        )
    )

    if not account:

        return None

    contract_end = datetime.strptime(
        str(account["contract_end"]),
        "%Y-%m-%d"
    )

    today = datetime.now()

    days_remaining = (
        contract_end - today
    ).days

    return {

        "contract_end":
        str(contract_end.date()),

        "days_remaining":
        days_remaining,

        "expiring_soon":
        days_remaining <= 30
    }

def get_seat_utilization(
    account_id: str
):

    account = (
        account_repo
        .get_account_by_id(
            account_id
        )
    )

    users = (
        user_repo
        .get_users_by_account(
            account_id
        )
    )

    seats = account["seat_count"]

    active_users = len([
        user
        for user in users
        if user["status"]
        == "Active"
    ])

    utilization = 0

    if seats > 0:

        utilization = round(
            (
                active_users
                / seats
            ) * 100,
            2
        )

    return {

        "seat_count":
        seats,

        "active_users":
        active_users,

        "utilization":
        utilization
    }

def get_customer_profile(
    account_id: str
):

    account = (
        account_repo
        .get_account_by_id(
            account_id
        )
    )

    users = (
        user_repo
        .get_users_by_account(
            account_id
        )
    )

    subscription = (
        subscription_repo
        .get_subscription(
            account_id
        )
    )

    return {

        "account":
        account,

        "users":
        users,

        "subscription":
        subscription
    }

def get_account_health(
    account_id: str
):

    account = (
        account_repo
        .get_account_by_id(
            account_id
        )
    )

    users = (
        user_repo
        .get_users_by_account(
            account_id
        )
    )

    seat_count = (
        account["seat_count"]
    )

    active_users = len([
        user
        for user in users
        if user["status"]
        == "Active"
    ])

    utilization = 0

    if seat_count > 0:

        utilization = (
            active_users
            / seat_count
        ) * 100

    contract = (
        get_contract_status(
            account_id
        )
    )

    score = 100

    if utilization < 20:

        score -= 20

    if contract[
        "days_remaining"
    ] < 30:

        score -= 25

    if account[
        "account_status"
    ] != "Active":

        score -= 40

    if score >= 80:

        health = "Healthy"

    elif score >= 60:

        health = "Warning"

    else:

        health = "At Risk"

    return {

        "health_score":
        score,

        "health_status":
        health,

        "seat_utilization":
        round(utilization, 2),

        "contract_days_remaining":
        contract["days_remaining"]
    }

def recommend_plan_upgrade(
    account_id: str
):

    account = (
        account_repo
        .get_account_by_id(
            account_id
        )
    )

    seat_data = (
        get_seat_utilization(
            account_id
        )
    )

    utilization = (
        seat_data["utilization"]
    )

    current_plan = (
        account["plan_tier"]
    )

    recommendation = None

    if utilization > 90:

        recommendation = (
            "Upgrade Recommended"
        )

    elif utilization > 75:

        recommendation = (
            "Consider Upgrade"
        )

    else:

        recommendation = (
            "Current Plan Sufficient"
        )

    return {

        "current_plan":
        current_plan,

        "seat_utilization":
        utilization,

        "recommendation":
        recommendation
    }

def get_churn_risk(
    account_id: str
):

    health = (
        get_account_health(
            account_id
        )
    )

    score = (
        health["health_score"]
    )

    if score >= 80:

        risk = "Low"

    elif score >= 60:

        risk = "Medium"

    else:

        risk = "High"

    return {

        "risk": risk,

        "health_score":
        score
    }

