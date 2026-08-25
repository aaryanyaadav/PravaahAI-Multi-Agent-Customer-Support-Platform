from src.agents.base.base_agent import (
    BaseAgent
)

from src.agents.escalation.escalation_prompt import (
    ESCALATION_SYSTEM_PROMPT
)
class EscalationAgent(
    BaseAgent
):

    def __init__(self):

        super().__init__(
            domain="escalation",
            system_prompt=ESCALATION_SYSTEM_PROMPT
        )