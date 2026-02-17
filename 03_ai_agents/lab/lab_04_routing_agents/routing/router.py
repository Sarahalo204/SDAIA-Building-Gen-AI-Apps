"""
Router Chain: Classify queries into domains, then filter tools.
Uses a cheap model for classification, saving tokens on the main call.
"""

import logging
from litellm import completion
from tools.registry import registry, Tool

logger = logging.getLogger(__name__)

# Define valid query domains (must match ROUTER_SYSTEM_PROMPT)


ROUTER_SYSTEM_PROMPT = """You are a query router. Classify the user's query
into exactly one domain. Respond with ONLY the domain name, nothing else.

Available domains:
- "financial": Stock prices, currency conversion, crypto, market analysis
- "academic": Research papers, scientific definitions, citations, studies
- "general": Weather, web search, calculations, general knowledge

If unsure, respond with "general"."""


class ToolRouter:
    """
    Routes queries to the appropriate tool subset using a cheap classifier.
    """

    def __init__(self, router_model: str = "gpt-4o-mini"):
        self.router_model = router_model
        self.valid_domains = ["financial", "academic", "general"]

    def classify(self, query: str) -> str:
        """
        Classify a query into a domain using a cheap, fast model.
        Returns the domain name string.
        """
        response = completion(
            model=self.router_model,
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            max_tokens=20,
            temperature=0,
            timeout=15,
        )

        domain = response.choices[0].message.content.strip().lower()
        domain = domain.strip('"').strip("'")  # Remove any quotes

        # Validate domain exists, fallback to "general"
        if domain not in self.valid_domains:
            logger.warning(f"Unknown domain '{domain}', falling back to 'general'")
            domain = "general"

        return domain

    def get_tools_for_domain(self, domain: str) -> list[Tool]:
        """Get the registered tools for a specific domain."""
        return registry.get_tools_by_category(domain)

    def route(self, query: str) -> tuple[str, list[Tool]]:
        """
        Full routing pipeline: classify then filter tools.
        Returns (domain, filtered_tools).
        """
        domain = self.classify(query)
        tools = self.get_tools_for_domain(domain)

        logger.info(f"Query classified as '{domain}' -> {len(tools)} tools selected")

        return domain, tools
