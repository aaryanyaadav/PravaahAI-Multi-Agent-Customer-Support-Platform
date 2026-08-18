from typing import Dict

from src.tools.definitions import ToolDefinition


class ToolRegistry:

    def __init__(self):

        self.tools: Dict[
            str,
            ToolDefinition
        ] = {}

    def register(
        self,
        tool: ToolDefinition
    ):

        self.tools[
            tool.name
        ] = tool

    def get_tool(
        self,
        tool_name: str
    ):

        return self.tools.get(
            tool_name
        )

    def get_tools_by_domain(
        self,
        domain: str
    ):

        return [

            tool

            for tool in self.tools.values()

            if tool.domain == domain
        ]

    def list_all_tools(self):

        return list(
            self.tools.keys()
        )