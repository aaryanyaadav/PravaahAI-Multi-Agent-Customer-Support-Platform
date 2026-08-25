from typing import Optional, Dict, Any
from src.agents.base.graph_builder import build_agent_graph
from src.tools.global_registry import tool_registry

class BaseAgent:
    def __init__(self, domain: str, system_prompt: str):
        self.domain = domain
        self.system_prompt = system_prompt
        self.graph = build_agent_graph()

    def invoke(self, query: str, shared_context: Optional[Dict[str, Any]] = None) -> str:
        tools = tool_registry.list_tools_for_domain(self.domain)
        initial_state = {
            "query": query,
            "domain": self.domain,
            "system_prompt": self.system_prompt,
            "messages": [],
            "available_tools": tools,
            "selected_tool": None,
            "tool_input": {},
            "tool_output": None,
            "final_answer": None,
            "iteration_count": 0,
            "shared_context": shared_context or {}
        }
        result = self.graph.invoke(initial_state)
        return result.get("final_answer") or "Could not resolve query."
