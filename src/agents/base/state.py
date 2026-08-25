# agents/base/state.py

from typing import TypedDict
from typing import List
from typing import Dict
from typing import Any


class AgentState(TypedDict):

    query: str

    domain: str

    messages: List[Dict]

    available_tools: List[Any]

    selected_tool: str

    tool_input: Dict

    tool_output: Any

    final_answer: str

    iteration_count: int

    shared_context: Dict[str, Any]