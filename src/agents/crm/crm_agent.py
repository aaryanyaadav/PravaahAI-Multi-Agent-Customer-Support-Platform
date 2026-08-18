from src.agents.base.base_agent import (
    BaseAgent
)

from src.agents.crm.crm_prompt import (
    CRM_SYSTEM_PROMPT
)


class CRMAgent(
    BaseAgent
):

    def __init__(self):

        super().__init__(
            domain="crm",
            system_prompt=CRM_SYSTEM_PROMPT
        )