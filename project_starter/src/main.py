import asyncio
import os
import sys

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

from src.agent.specialists import create_researcher, create_analyst, create_writer
from src.observability.tracer import tracer # TODO: Unleash the tracer
from src.observability.cost_tracker import CostTracker
import src.tools.search_tool

# Load environment variables
load_dotenv()

def print_separator(title: str):
    print(f"\n{'-'*60}")
    print(f" {title.upper()}")
    print(f"{'-'*60}\n")

async def main():
    """
    Main entry point for the AI Agent system.
    """
    # 1. Get the query
    if len(sys.argv) < 2:
        print("Usage: python -m src.main \"Your research query\"")
        sys.exit(1)

    query = sys.argv[1]
    print(f"Starting research on: {query}")

    # TODO: Initialize your agents here
    # Use the Factory Pattern to create agents.
    # The 'create_researcher' function (and others) acts as a factory, encapsulating 
    # the creation logic (prompt selection, tool assignment) for each agent type.
    # researcher = create_researcher()
    # analyst = create_analyst()
    # writer = create_writer()
    
    # TODO: Create the orchestrator or main loop
    # In the final project, we might use an ArchitectureDecisionEngine here to decide
    # which agent architecture (Single vs Multi-Agent) to run. 
    # For this starter, you can implement a simple linear chain (Researcher -> Analyst -> Writer)
    # or a loop.
    # ...
    
    try:
        print("  Initializing Agents...")
        researcher = create_researcher()
        analyst = create_analyst()
        writer = create_writer()
        print("Agents initialized successfully.")
    except Exception as e:
        print(f" Error initializing agents: {e}")
        return
    
    #1
    print_separator("1.RESEARCHER AGENT")
    print(f"🔍 Researcher is finding information about: {query}...")
    
    research_result = await researcher.run(query)
    
    if "Error" in str(research_result.get("answer", "")):
        print(f" Research failed: {research_result['answer']}")
        return

    print(f"Research Complete. Steps taken: {research_result['steps']}")
    snippet = research_result['answer'][:200].replace('\n', ' ') + "..."
    print(f" Output Snippet: {snippet}")

    #2
    print_separator("2.ANALYST AGENT")
    print(" Analyst is processing the data...")
    
    analyst_input = (
        f"Original User Query: {query}\n\n"
        f"Raw Research Data Provided by Researcher:\n{research_result['answer']}"
    )
    
    analysis_result = await analyst.run(analyst_input)
    
    print(f" Analysis Complete. Steps taken: {analysis_result['steps']}")
    
    #3
    print_separator("3.WRITER AGENT")
    print(" Writer is compiling the final report...")
    
    writer_input = (
        f"Topic: {query}\n\n"
        f"Strategic Analysis:\n{analysis_result['answer']}"
    )
    
    final_output = await writer.run(writer_input)
    
    print(f" Writing Complete. Steps taken: {final_output['steps']}")
    #4
    print_separator("Final report")
    print(final_output['answer'])
    
    print_separator("Session summary")
    
    total_cost = (
        research_result.get('total_cost', 0.0) +
        analysis_result.get('total_cost', 0.0) +
        final_output.get('total_cost', 0.0)
    )
    
    print(f" Total Estimated Cost: ${total_cost:.6f}")
    print(f" Trace IDs:")
    print(f"   - Research: {research_result.get('trace_id')}")
    print(f"   - Analysis: {analysis_result.get('trace_id')}")
    print(f"   - Writing:  {final_output.get('trace_id')}")
    print(f"\n{'-'*60}\n")


    print("Project Starter: Not implemented yet. Check the TODOs!")

if __name__ == "__main__":
    asyncio.run(main())
