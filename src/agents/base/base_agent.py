# agents/base/base_agent.py

from src.agents.base.graph_builder import (
    build_agent_graph
)

from src.agents.base.tool_router import (
    ToolRouter
)


class BaseAgent:

    def __init__(
        self,
        domain: str,
        system_prompt: str = "You are an expert support agent."
    ):

        self.domain = domain

        self.system_prompt = system_prompt

        self.graph = (
            build_agent_graph()
        )

    def invoke(
        self,
        query: str,
        shared_context: dict = None
    ):

        tools = (
            ToolRouter
            .get_domain_tools(
                self.domain
            )
        )

        state = {

            "query": query,

            "domain":
            self.domain,

            "system_prompt":
            self.system_prompt,

            "messages": [],

            "available_tools":
            tools,

            "selected_tool":
            "",

            "tool_input": {},

            "tool_output":
            None,

            "final_answer":
            "",

            "iteration_count":
            0,

            "shared_context":
            shared_context or {}
        }

        result = (
            self.graph.invoke(
                state
            )
        )

        return result[
            "final_answer"
        ]