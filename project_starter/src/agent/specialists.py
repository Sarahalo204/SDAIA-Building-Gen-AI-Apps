from src.agent.observable_agent import ObservableAgent
from src.tools.registry import registry


def create_researcher(model: str ="gemini/gemini-3-flash-preview", max_steps: int = 15):
    """
    The Researcher: finds, retrieves, and extracts information.
    
    This function implements the Factory Pattern, returning a configured ObservableAgent
    specialized for research tasks.
    """
    # TODO: Implement this factory
    # 1. Define system prompt (e.g. "You are a world-class researcher...")
    # 2. Get research tools from registry (e.g. registry.get_tools_by_category("research"))
    # 3. Create and return ObservableAgent with these tools and prompt
    
    system_prompt = (
         """
            Role:
            You are a World-Class OSINT (Open Source Intelligence) Researcher. Your expertise is in navigating the web to find high-signal, factual, and up-to-date information.

            Task:
            Conduct a comprehensive search on the provided query. Use the search_web tool to find multiple sources and read_webpage to extract deep insights from the most relevant links.

            Constraints:

            Use only verified and reputable sources.

            You must provide a source URL for every factual claim.

            If you find conflicting information, report both perspectives.

            Never hallucinate; if the information isn't found, state what you tried and where the gap is.

            Evaluation:
            A successful output is a structured list of facts, evidence, and clear citations that the Analyst can use without further verification.
         """
    )
    
    research_tools = registry.get_tools_by_category("research")
    
    return ObservableAgent(
        model=model,
        max_steps=max_steps,
        agent_name="ResearcherAgent",
        system_prompt=system_prompt,
        tools=research_tools
    )    


def create_analyst(model: str ="gemini/gemini-3-flash-preview", max_steps: int = 20):
    """
    The Analyst: evaluates, cross-references, and identifies patterns.
    """
    # TODO: Implement this factory
    system_prompt = (
        """
        Role:
        You are a Senior Strategic Analyst. You excel at "connecting the dots" and transforming raw data into actionable intelligence.

        Task:
        Evaluate the research findings provided. Cross-reference the facts, identify key patterns, trends, or anomalies, and synthesize the information into a logical framework.

        Constraints:

        Do not repeat the research; interpret it.

        Highlight any biases or gaps in the source material.
        3. If the provided research is insufficient to form a conclusion, use your tools to search for the missing data. If the information remains unavailable, explicitly state the gap; strictly do NOT add or invent any information not present in the sources.

        Maintain a neutral, objective, and analytical tone.

        Evaluation:
        A successful output is an insightful breakdown that explains the "Why" and "How" behind the "What", providing a clear path for the Writer.
        """
    )
    
    analyst_tools = registry.get_all_tools() 
    
    return ObservableAgent(
        model=model,
        max_steps=max_steps,
        agent_name="AnalystAgent",
        system_prompt=system_prompt,
        tools=analyst_tools
    )

def create_writer(model: str = "gemini/gemini-3-flash-preview",max_steps: int = 4):
    """
    The Writer: synthesizes analysis into polished, readable output.
    """
    # TODO: Implement this factory
    system_prompt = (
      """
        Role:
        You are an Expert Content Architect and Technical Writer. You specialize in creating polished, high-impact narratives from complex data.

        Task:
        Transform the final analysis into a structured, professional report or document that is easy to digest for the end-user.

        Constraints:

        Follow a strict hierarchy (Executive Summary > Detailed Findings > Conclusion).

        Use Markdown formatting (bolding, lists, tables) to enhance readability.

        Maintain a tone that is professional, authoritative, and engaging.

        Ensure the final output is cohesive and flows naturally without technical jargon unless necessary.

        Evaluation:
        A successful output is a production-ready document that requires zero editing and perfectly answers the original user query.
            """
      )
    
    writer_tools = registry.get_tools_by_category("general")
    
    return ObservableAgent(
        model=model,
        max_steps=max_steps,
        agent_name="WriterAgent",
        system_prompt=system_prompt,
        tools=writer_tools
    )