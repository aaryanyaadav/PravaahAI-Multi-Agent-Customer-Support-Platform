import json

from llm.groq_client import (
    GroqClient
)

client = GroqClient()

def reason_node(
    state
):

    tools = state["available_tools"]

    # Format tools list in a compact format to save tokens
    tool_descriptions_list = []
    for tool in tools:
        tool_descriptions_list.append(f"- {tool.name}: {tool.description}")
    tool_descriptions_str = "\n".join(tool_descriptions_list)

    # Format tool history so the agent can see the results of previous actions
    history_str = ""
    if state.get("messages"):
        history_lines = []
        for msg in state["messages"]:
            history_lines.append(f"- Tool: {msg['tool']}\n  Output: {msg['output']}")
        history_str = "Tool Execution History:\n" + "\n".join(history_lines) + "\n\n"

    # Format shared memory context to be visible to the LLM
    shared_context_str = ""
    shared_context = state.get("shared_context")
    if shared_context:
        shared_context_lines = []
        for k, v in shared_context.items():
            if v:
                shared_context_lines.append(f"- {k}: {v}")
        if shared_context_lines:
            shared_context_str = "Shared context from other agents:\n" + "\n".join(shared_context_lines) + "\n\n"

    prompt = f"""
Choose a tool to retrieve details, or generate a final answer if fully resolved by history. Return ONLY JSON.

Tools:
{tool_descriptions_str}

{shared_context_str}{history_str}Query: {state['query']}

JSON Format:
{{
  "action": "tool" | "final",
  "tool_name": "name",
  "tool_input": {{}},
  "answer": "answer_text"
}}
"""

    system_prompt = state.get("system_prompt", "You are an expert support agent.")
    system_prompt_formatted = f"{system_prompt.strip()} Return only JSON."

    response = client.invoke(
        system_prompt=system_prompt_formatted,
        user_prompt=prompt
    )

    if not response.success:
        raise ValueError(f"LLM invocation failed: {response.content}")

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError as e:
        import re
        match = re.search(r"```json\s*(\{.*?\})\s*```", response.content, re.DOTALL)
        if not match:
            match = re.search(r"```\s*(\{.*?\})\s*```", response.content, re.DOTALL)
        
        cleaned_content = None
        if match:
            cleaned_content = match.group(1).strip()
        else:
            start = response.content.find('{')
            end = response.content.rfind('}')
            if start != -1 and end != -1 and end > start:
                cleaned_content = response.content[start:end+1].strip()
        
        if cleaned_content:
            try:
                result = json.loads(cleaned_content)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse LLM response as JSON. Content was:\n{response.content}") from e
        else:
            raise ValueError(f"Failed to parse LLM response as JSON. Content was:\n{response.content}") from e

    # Update iteration count to prevent infinite loops

    state["iteration_count"] = state.get("iteration_count", 0) + 1

    # Accumulate token usage in the shared context
    if "shared_context" in state and isinstance(state["shared_context"], dict):
        if "tokens_used" not in state["shared_context"]:
            state["shared_context"]["tokens_used"] = 0
        state["shared_context"]["tokens_used"] += getattr(response, "tokens_used", 0)

    if result["action"] == "final":
        state["final_answer"] = result["answer"]
    else:
        state["selected_tool"] = result["tool_name"]
        state["tool_input"] = result["tool_input"]

    return state

from src.tools.executor import (
    ToolExecutor
)

from src.tools.global_registry import (
    tool_registry
)

executor = ToolExecutor(
    tool_registry
)
def tool_node(
    state
):
    result = executor.execute(
        state["selected_tool"],
        **state["tool_input"]
    )

    output_val = result.data if result.success else f"Error: {result.error}"

    state["tool_output"] = (
        output_val
    )

    state["messages"].append({
        "tool":
        state["selected_tool"],
        "output":
        output_val
    })

    return state






# Decison node 


def should_continue(
    state
):

    if state.get(
        "final_answer"
    ) or state.get("iteration_count", 0) >= 5:

        return "end"

    return "tool"
