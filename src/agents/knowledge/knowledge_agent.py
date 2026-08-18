from src.agents.base.base_agent import (
    BaseAgent
)

from src.agents.knowledge.knowledge_prompt import (
    KNOWLEDGE_SYSTEM_PROMPT
)


class KnowledgeAgent(
    BaseAgent
):

    def __init__(self):

        super().__init__(
            domain="knowledge",
            system_prompt=KNOWLEDGE_SYSTEM_PROMPT
        )