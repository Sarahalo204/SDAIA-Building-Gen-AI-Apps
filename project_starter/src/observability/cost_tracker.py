import logging
from dataclasses import dataclass, field
from typing import Optional
from litellm import completion_cost

logger = logging.getLogger(__name__)

@dataclass
class StepCost:
    step_number: int
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    is_tool_call: bool = False

@dataclass
class QueryCost:
    query: str
    steps: list[StepCost] = field(default_factory=list)
    total_cost_usd: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def add_step(self, step: StepCost):
        self.steps.append(step)
        self.total_cost_usd += step.cost_usd
        self.total_input_tokens += step.input_tokens
        self.total_output_tokens += step.output_tokens

class CostTracker:
    """
    Tracks costs across agent executions.
    """
    def __init__(self):
        self.queries: list[QueryCost] = []
        self._current_query: QueryCost | None = None

    def start_query(self, query: str):
        self._current_query = QueryCost(query=query)
        
    def add_cost(self, cost: float):
        """Add cost manually (used by Agent)."""
        if self._current_query:
            self._current_query.total_cost_usd += cost
        else:
            self.start_query("unknown_query")
            self._current_query.total_cost_usd += cost 
            
    def get_total_cost(self) -> float:
        """Get current total cost (used by Agent)."""
        if self._current_query:
            return self._current_query.total_cost_usd
        return 0.0           

    def log_completion(self, step_number: int, response, is_tool_call: bool = False):
        """
        Log a completion response's cost.
        """
        # TODO: Implement this method
        # 1. Check if _current_query exists
        # 2. Extract usage stats from response
        # 3. Calculate cost (use litellm.completion_cost or fallback)
        # 4. create StepCost and add to query
        if not self._current_query:
            return
        
        try:                
            if isinstance(response, dict):
                usage = response.get("usage", {})
                model = response.get("model", "unknown")
            else:
                usage = getattr(response, "usage", {})
                model = getattr(response, "model", "unknown")    

            prompt_tokens = getattr(usage, "prompt_tokens", 0) or usage.get("prompt_tokens", 0)
            completion_tokens = getattr(usage, "completion_tokens", 0) or usage.get("completion_tokens", 0)
            

            cost = completion_cost(completion_response=response)
            step = StepCost(
                step_number=step_number,
                model=model,
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
                cost_usd=cost,
                is_tool_call=is_tool_call
            )
            self._current_query.add_step(step)

        except Exception as e:
            logger.warning(f"Failed to log completion cost: {e}")

    def end_query(self):
        if self._current_query:
            self.queries.append(self._current_query)
            self._current_query = None

    def print_cost_breakdown(self):
        # TODO: Print detailed cost breakdown
        target = self._current_query or (self.queries[-1] if self.queries else None)
        if not target:
            print("No cost data available.")
            return

        print(f"\n--- Cost Breakdown for: {target.query[:50]}... ---")
        print(f"Total Cost: ${target.total_cost_usd:.6f}")
        print(f"Total Tokens: {target.total_input_tokens + target.total_output_tokens} "
              f"(In: {target.total_input_tokens}, Out: {target.total_output_tokens})")
        print(f"Steps: {len(target.steps)}")

