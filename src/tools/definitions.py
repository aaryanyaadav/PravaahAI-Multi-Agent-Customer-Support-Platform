from dataclasses import dataclass
from typing import Callable


@dataclass
class ToolDefinition:

    name: str

    description: str

    domain: str

    function: Callable