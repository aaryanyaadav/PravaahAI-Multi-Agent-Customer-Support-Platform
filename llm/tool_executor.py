from typing import Dict
from typing import Callable


class ToolExecutor:

    def __init__(self):

        self.tools = {}

    def register_tool(
        self,
        name: str,
        tool: Callable
    ):

        self.tools[name] = tool

    def execute(
        self,
        tool_name: str,
        **kwargs
    ):

        if tool_name not in self.tools:

            raise Exception(
                f"Tool not found: {tool_name}"
            )

        return self.tools[
            tool_name
        ](**kwargs)