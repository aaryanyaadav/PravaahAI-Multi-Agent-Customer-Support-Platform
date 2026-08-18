from src.agents.base.base_agent import (
    BaseAgent
)

from src.agents.billing.billing_prompt import (
    BILLING_SYSTEM_PROMPT
)


class BillingAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            domain="billing",
            system_prompt=BILLING_SYSTEM_PROMPT
        )