from pydantic import BaseModel
from typing import Any


class ToolResult(BaseModel):

    success: bool

    tool_name: str

    data: Any = None

    error: str | None = None