from src.tools.result import ToolResult


class ToolExecutor:

    def __init__(
        self,
        registry
    ):

        self.registry = registry

    def execute(
        self,
        tool_name: str,
        **kwargs
    ) -> ToolResult:

        tool = (
            self.registry
            .get_tool(tool_name)
        )

        if not tool:

            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=f"Tool not found: {tool_name}"
            )

        try:

            result = (
                tool.function(
                    **kwargs
                )
            )

            return ToolResult(
                success=True,
                tool_name=tool_name,
                data=result
            )

        except Exception as e:

            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=str(e)
            )