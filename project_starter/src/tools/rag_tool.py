from src.tools.registry import registry
from src.rag.engine import rag_engine

@registry.register(
    name="search_knowledge_base", 
    description="Search the internal knowledge base (PDFs & Regulations). Returns relevant snippets with similarity scores.",
    category="specialized"
)
def search_knowledge_base(query: str) -> str:
    """
    Search wrapper that formats results for the Writer Agent.
    """
    results = rag_engine.search(query, n_results=8) # top-k
    
    if not results:
        return "No relevant information found in the knowledge base."
    
    formatted_output = "Found the following relevant excerpts:\n\n"
    for i, res in enumerate(results, 1):
        formatted_output += (
            f"--- Result {i} (Similarity: {res['score']}) ---\n"
            f"Source: {res['source']}\n"
            f"Content: \"{res['text']}\"\n\n"
        )
    
    return formatted_output