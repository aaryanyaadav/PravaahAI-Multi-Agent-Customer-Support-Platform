
from langgraph.graph import (
    StateGraph,
    END
)

from src.agents.base.nodes import (
    reason_node,
    tool_node,
    should_continue
)

from src.agents.base.state import (
    AgentState
)

def build_agent_graph():

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "reason",
        reason_node
    )

    graph.add_node(
        "tool",
        tool_node
    )

    graph.set_entry_point(
        "reason"
    )

    graph.add_conditional_edges(

        "reason",

        should_continue,

        {

            "tool":
            "tool",

            "end":
            END
        }
    )

    graph.add_edge(
        "tool",
        "reason"
    )

    return (
        graph.compile()
    )

