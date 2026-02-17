"""
Semantic Tool Selector: Use embeddings to dynamically match
user queries to the most relevant tools.
"""

import logging
import numpy as np
from litellm import embedding
from tools.registry import registry, Tool

logger = logging.getLogger(__name__)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    dot_product = np.dot(a_arr, b_arr)
    norm_product = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if norm_product == 0:
        return 0.0
    return float(dot_product / norm_product)


def get_embedding_vector(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Get embedding vector for a text string using LiteLLM."""
    response = embedding(model=model, input=[text])
    return response.data[0]["embedding"]


class SemanticToolSelector:
    """
    Dynamically select tools based on semantic similarity
    between query and tool descriptions.
    """

    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        self.embedding_model = embedding_model
        self._tool_embeddings: dict[str, list[float]] = {}
        self._indexed = False

    def build_index(self):
        """
        Embed all registered tool descriptions.
        Call this once at startup (or when tools change).
        """
        tools = registry.get_all_tools()
        if not tools:
            logger.warning("No tools registered.")
            return

        logger.info(f"Indexing {len(tools)} tools...")

        # Batch all descriptions for a single embedding call
        descriptions = []
        tool_names = []
        for tool in tools:
            # Include both name and description for richer embeddings
            text = f"{tool.name}: {tool.description}"
            descriptions.append(text)
            tool_names.append(tool.name)

        # Single batch embedding call (efficient)
        response = embedding(
            model=self.embedding_model,
            input=descriptions,
        )

        for i, tool_name in enumerate(tool_names):
            self._tool_embeddings[tool_name] = response.data[i]["embedding"]

        self._indexed = True
        logger.info(f"Indexed {len(tools)} tools.")

    def select_tools(self, query: str, top_k: int = 5) -> list[tuple[Tool, float]]:
        """
        Select the top-K most relevant tools for a query.

        Returns:
            List of (Tool, similarity_score) tuples, sorted by relevance.
        """
        if not self._indexed:
            self.build_index()

        # Embed the query
        query_embedding = get_embedding_vector(query, self.embedding_model)

        # Score each tool
        scores = []
        for tool_name, tool_embedding in self._tool_embeddings.items():
            similarity = cosine_similarity(query_embedding, tool_embedding)
            tool = registry.get_tool(tool_name)
            if tool:
                scores.append((tool, similarity))

        # Sort by similarity (highest first) and return top K
        scores.sort(key=lambda x: x[1], reverse=True)
        top_tools = scores[:top_k]

        logger.info(f"Query: '{query[:50]}...'")
        for tool, score in top_tools:
            logger.debug(f"  {tool.name}: {score:.4f}")

        return top_tools

    def get_tool_schemas(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Convenience method: get OpenAI-format schemas for the top-K tools.
        Ready to pass directly to litellm.completion(tools=...).
        """
        selected = self.select_tools(query, top_k)
        return [tool.to_openai_schema() for tool, _score in selected]
