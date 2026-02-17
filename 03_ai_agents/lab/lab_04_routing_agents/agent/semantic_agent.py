"""
An agent that uses semantic tool selection for each query.
Best for large, diverse tool registries (100+ tools).
"""

import json
from litellm import completion
from routing.semantic_router import SemanticToolSelector

SYSTEM_PROMPT = """You are a research assistant agent. You solve tasks by
reasoning step-by-step and using tools when needed.

You have access to a set of tools.
ALWAYS use the provided tools to gather information or perform actions.
Never fabricate tool results.

When you have enough information to answer the user's question,
respond with your final answer."""


class SemanticAgent:
    """Agent with dynamic, embedding-based tool selection."""

    def __init__(
        self,
        model: str = "gpt-4o",
        top_k_tools: int = 5,
        max_steps: int = 10,
    ):
        self.model = model
        self.top_k = top_k_tools
        self.max_steps = max_steps
        self.selector = SemanticToolSelector()
        self.selector.build_index()

    def run(self, user_query: str) -> dict:
        # Dynamically select tools for this query
        tools_schema = self.selector.get_tool_schemas(user_query, self.top_k)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]

        for step in range(self.max_steps):
            response = completion(
                model=self.model,
                messages=messages,
                tools=tools_schema if tools_schema else None,
                tool_choice="auto" if tools_schema else None,
                max_tokens=1024,
            )

            message = response.choices[0].message
            messages.append(message)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    from tools.registry import registry
                    tool = registry.get_tool(fn_name)
                    if tool:
                        result = str(tool.execute(**fn_args))
                    else:
                        result = f"Error: Tool '{fn_name}' not found."

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": fn_name,
                        "content": result,
                    })

            elif message.content:
                return {
                    "answer": message.content,
                    "tools_available": [s["function"]["name"] for s in tools_schema],
                    "total_steps": step + 1,
                }

        return {
            "answer": "[Agent reached maximum steps]",
            "total_steps": self.max_steps,
        }
