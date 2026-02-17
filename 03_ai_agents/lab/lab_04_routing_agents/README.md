# Lab 04: Routing & Semantic Agents

This lab explores advanced agent patterns using specialized routers to direct queries to the right tools.

## Contents

- **`routing/router.py`**: A classifier-based router using a small LLM (e.g., GPT-4o-mini) to categorize queries into domains (Financial, Academic, General).
- **`routing/semantic_router.py`**: An embedding-based router that selects tools based on semantic similarity to the query.
- **`agent/routed_agent.py`**: An agent that uses the classifier router to filter its toolset before execution, reducing context window usage.
- **`agent/semantic_agent.py`**: An agent that dynamically retrieves the top-k most relevant tools for every query using embeddings.

## How to use

Ensure you have your environment set up with `litellm` and `pydantic`.

You can import these agents and run them with queries to see how they select different subsets of tools compared to a standard agent.
