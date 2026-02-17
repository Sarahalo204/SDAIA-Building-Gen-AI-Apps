"""
A ReactAgent that routes queries to domain-specific tool subsets.
"""

import json
from litellm import completion
from routing.router import ToolRouter

REACT_SYSTEM_PROMPT = """You are a research assistant agent. You solve tasks by
reasoning step-by-step and using tools when needed.

You have access to a set of tools.
ALWAYS use the provided tools to gather information or perform actions.
Never fabricate tool results.

When you have enough information to answer the user's question,
respond with your final answer."""


class RoutedAgent:
    """
    An agent that uses routing to select tools before execution.
    This keeps the context window lean and improves tool selection accuracy.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        router_model: str = "gpt-4o-mini",
        max_steps: int = 10,
    ):
        self.model = model
        self.router = ToolRouter(router_model=router_model)
        self.max_steps = max_steps

    def run(self, user_query: str) -> dict:
        """Execute with routing: classify → filter tools → run agent loop."""

        # Step 1: Route the query
        domain, tools = self.router.route(user_query)
        tools_schema = [tool.to_openai_schema() for tool in tools]

        print(f"[RoutedAgent] Domain: {domain}, "
              f"Tools: {[t.name for t in tools]}")

        # Step 2: Run the agent loop with filtered tools only
        messages = [
            {"role": "system", "content": REACT_SYSTEM_PROMPT},
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

            # Handle tool calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    # Execute tool from filtered set
                    tool = next((t for t in tools if t.name == fn_name), None)
                    if tool:
                        result = str(tool.execute(**fn_args))
                    else:
                        result = f"Error: Tool '{fn_name}' not available."

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": fn_name,
                        "content": result,
                    })

            elif message.content:
                return {
                    "answer": message.content,
                    "domain": domain,
                    "tools_used": [t.name for t in tools],
                    "total_steps": step + 1,
                }

        return {
            "answer": "[Agent reached maximum steps]",
            "domain": domain,
            "tools_used": [t.name for t in tools],
            "total_steps": self.max_steps,
        }
