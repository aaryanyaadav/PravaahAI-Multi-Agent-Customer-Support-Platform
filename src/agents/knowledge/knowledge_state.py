from typing import TypedDict
from typing import List
from typing import Dict
from typing import Any


class KnowledgeState(TypedDict):

    query: str

    system_prompt: str

    selected_tool: str

    tool_input: Dict

    retrieved_context: Any

    final_answer: str

    messages: List[Dict]