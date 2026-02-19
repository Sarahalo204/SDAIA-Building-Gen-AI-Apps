import asyncio
import os
import sys
import io
import logging

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

from src.agent.specialists import create_researcher, create_analyst, create_writer
from src.observability.tracer import tracer # TODO: Unleash the tracer
from src.observability.cost_tracker import CostTracker
import src.tools.search_tool
from src.rag.engine import rag_engine
import src.tools.rag_tool
from src.tools.registry import registry


logging.basicConfig(
    level=logging.INFO,
    format='\n[TOOL EXECUTION] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
    )

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("litellm").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.WARNING)
    
def print_tools():
    tools = registry.get_all_tools()
    if not tools:
        print("No tools registered!")
        return

    print("\n--- REGISTERED TOOLS ---\n")
    for tool in tools:
        categories = [cat for cat, names in registry._categories.items() if tool.name in names]
        category = categories[0] if categories else "uncategorized"
        print(f"Name: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Category: {category}")
        print("-"*40)
    print("\n------------------------\n")
    
    
def print_separator(title: str):
    print(f"\n{'-'*60}")
    print(f" {title.upper()}")
    print(f"{'-'*60}\n")

def setup_knowledge_base():
    """
    تجهيز قاعدة المعرفة (RAG): قراءة الرابط والمجلد الكامل للـ PDFs.
    """
    print_separator("0. KNOWLEDGE BASE INGESTION")
    
    target_url = "https://www.hrsd.gov.sa/knowledge-centre/decisions-and-regulations"
    rag_engine.ingest_url(target_url)
    

    pdf_directory = os.path.join("src", "documents")
    
    if os.path.exists(pdf_directory):
        rag_engine.ingest_directory(pdf_directory)
    else:
        print(f"Warning: Directory not found: {pdf_directory}")
        
        print("Please ensure your PDFs (r1.pdf, r2.pdf...) are in 'src/documents/'")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.main \"write your question here\"")
        sys.exit(1)
        
    print_tools()
        
    query = sys.argv[1]
    
    setup_knowledge_base()
    
    print(f"\nStarting Multi-Agent HR System for: {query}")

    try:
        researcher = create_researcher()
        analyst = create_analyst()
        writer = create_writer()
    except Exception as e:
        print(f"Error initializing agents: {e}")
        return
    #1
    print_separator("1. RESEARCHER (RAG + WEB)")
    research_result = await researcher.run(query)
    print(f"Research Output: {research_result['answer'][:300]}...\n")
    #2
    print_separator("2. ANALYST (LOGIC)")
    analyst_input = (
        f"User Query: {query}\n\n"
        f"Research Data (Regulations found):\n{research_result['answer']}"
    )
    analysis_result = await analyst.run(analyst_input)
    print(f"Analysis Output: {analysis_result['answer'][:300]}...\n")
    #3
    print_separator("3. WRITER (FINAL REPORT)")
    writer_input = (
        f"Original Query: {query}\n\n"
        f"Legal Analysis:\n{analysis_result['answer']}"
    )
    final_output = await writer.run(writer_input)
    
    print_separator("FINAL RESPONSE")
    print(final_output['answer'])
    print_separator("SESSION END")

if __name__ == "__main__":
    asyncio.run(main())