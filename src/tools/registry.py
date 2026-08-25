from typing import Dict, List, Callable, Any
from src.tools.definitions import ToolDefinition
from src.tools.result import ToolResult

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, name: str, description: str, domain: str, function: Callable):
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            domain=domain,
            function=function
        )

    def get_tool(self, name: str) -> ToolDefinition:
        return self._tools.get(name)

    def list_tools_for_domain(self, domain: str) -> List[ToolDefinition]:
        return [tool for tool in self._tools.values() if tool.domain == domain]

    def list_all_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())
