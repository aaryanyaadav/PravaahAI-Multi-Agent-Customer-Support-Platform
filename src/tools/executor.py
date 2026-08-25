from src.tools.registry import ToolRegistry
from src.tools.result import ToolResult

class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        tool_def = self.registry.get_tool(tool_name)
        if not tool_def:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                data=None,
                error=f"Tool '{tool_name}' not found in registry."
            )
        try:
            result = tool_def.function(**kwargs)
            return ToolResult(
                success=True,
                tool_name=tool_name,
                data=result,
                error=None
            )
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                data=None,
                error=str(e)
            )
