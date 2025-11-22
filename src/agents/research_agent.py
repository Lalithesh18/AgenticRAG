from typing import List
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import BaseTool
from llama_index.core.llms import LLM


RESEARCH_AGENT_PROMPT = """You are a Research Specialist AI agent.

Your role is to gather high quality information from the web using semantic search.

Key responsibilities:
1. Use search_web tool to find relevant sources on topics.
2. Use the get_content tool to fetch detailed information from specific URLs.
3. Use the find_similar tool to discover related sources.
4. Focus on finding authoritative information to support analysis.
5. Gather comprehensive, recent and relevant sources.

When researching:
- Formulate clear, specific search queries.
- Aim for diverse, high-quality sources. 
- Extract key information from results.
- Provide URLs and citations for all sources.

Always prioritize accuracy and relevance. Your research will be used by an Analysis Agent to synthesize insights.   
"""

def create_research_agent(
    llm: LLM,
    tools: List[BaseTool],
    verbose: bool = True
) -> ReActAgent:
    agent = ReActAgent.from_tools(
        tools = tools,
        llm=llm,
        verbose=verbose,
        context = RESEARCH_AGENT_PROMPT,
        max_iterations = 10
    )

    return agent