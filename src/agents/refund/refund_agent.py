# agents/refund/refund_agent.py

from src.agents.base.base_agent import (
    BaseAgent
)

from src.agents.refund.refund_prompt import (
    REFUND_SYSTEM_PROMPT
)


class RefundAgent(
    BaseAgent
):

    def __init__(self):

        super().__init__(
            domain="refund",
            system_prompt=REFUND_SYSTEM_PROMPT
        )
