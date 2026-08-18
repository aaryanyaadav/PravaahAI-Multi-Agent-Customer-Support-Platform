
from src.tools.global_registry import (
    tool_registry
)


class ToolRouter:

    @staticmethod
    def get_domain_tools(
        domain: str
    ):

        return (
            tool_registry
            .get_tools_by_domain(
                domain
            )
        )