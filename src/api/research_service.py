import os
import sys 

from typing import Dict, Any, AsyncGenerator
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llama_index.llms.cerebras import Cerebras
from tools.exa_tools import ExaSearchTools, create_search_tool,create_content_tool,create_similar_tool
from tools.analysis_tools import AnalysisTools,create_summarize_tool,create_compare_tool,create_insights_tool
from agents.research_agent import create_research_agent
from agents.analysis_agent import create_analysis_agent
from research_workflows.research_workflow import ResearchWorkflow
from .models import StreamChunk

class ResearchService:
    def __init__(self):
        self.workflow = None
        self.initialized = False
        self.llm = None
        self.exa_tools = None
        self.analysis_tools = None

    async def initialize(self):
        if self.initialized:
            return
        
        cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
        exa_api_key = os.getenv("EXA_API_KEY")
        model_name = os.getenv("CEREBRAS_MODEL", "llama3.3-70b")
        
        if not cerebras_api_key:
            raise ValueError("Cerebras API key not found in environment variables.")
        if not exa_api_key:
            raise ValueError("Exa API key not found in environment variables.")
        
        self.llm = Cerebras(
            api_key=cerebras_api_key,
            temperature=0.3,
            model=model_name
            )
        
        self.exa_tools = ExaSearchTools(exa_api_key=exa_api_key)
        self.analysis_tools = AnalysisTools()

        research_tools_list = [
            create_search_tool(self.exa_tools),
            create_content_tool(self.exa_tools),
            create_similar_tool(self.exa_tools)
        ]

        analysis_tools_list = [
            create_summarize_tool(self.analysis_tools),
            create_compare_tool(self.analysis_tools),
            create_insights_tool(self.analysis_tools)
        ]

        research_agent = create_research_agent(
            llm=self.llm, 
            tools=research_tools_list,
            verbose=False
            )
        analysis_agent = create_analysis_agent(llm=self.llm, tools=analysis_tools_list, verbose=False)

        self.workflow = ResearchWorkflow(
            research_agent=research_agent,
            analysis_agent=analysis_agent,
            verbose=False
        )

        async def shutdown():
            self.initialized = False
            self.llm = None
            self.workflow = None
        
        async def execute_query(self, query: str, num_results: int = 5) -> Dict[str, Any]:
            if not self.initialized:
                raise RuntimeError("Research Service not initialized. Call 'initialize' before executing queries.")
            
            original_search = self.exa_tools.search_web
            def custom_search(query: str, n_results: int = num_results, **kwargs): #args are tuple of arguements fed to the function accepting **args; kwargs are keyword arguements which are accepted into a dictionary when used/fed into a function using **kwargs
                return original_search(query, n_results, **kwargs)
            
            self.exa_tools.search_web = custom_search

            try:
                result = await self.workflow.run(query=query)
                sources = []
                return {
                    "answer": str(result),
                    "sources": sources,
                }
            finally:
                self.exa_tools.search_web = original_search

            
    async def execute_query_streaming(
        self,
        query: str,
        num_results: int = 5
    ) -> AsyncGenerator[StreamChunk, None]:
        
        if not self.initialized:
            raise RuntimeError("Research Service not initialized. Call 'initialize' before executing queries.")
        
        yield StreamChunk(
            type="research_start",
            content="Starting research on {query}",
            metadata={"num_results": num_results}
        )

        try:
            yield StreamChunk(
                type="research_update",
                content="Searching the web for relevant sources...",
                metadata={"stage": "search"}
            )

            search_results = self.exa_tools.search_web(query, n_results=num_results)

            if "error" in search_results:
                yield StreamChunk(
                    type="research_update",
                    content=f"Found {search_results.get("num_results",0)} sources",
                    metadata={
                        "stage": "search_complete",
                        "num_results": search_results.get("num_results",0)
                    }
                )
            yield StreamChunk(
                type="analysis_start",
                content="Starting analysis of gathered information...",
                metadata={"stage": "analysis"} 
            )

            result = await self.workflow.run(query=query)

            yield StreamChunk(
                type="analysis_complete",
                content=str(result),
                metadata={"stage": "complete", "sources": search_results.get("results", [])}
            )

        except Exception as e:
            yield StreamChunk(
                type="error",
                content=f"Error during research: {str(e)}",
                metadata={"error": str(e)}
            )
                
            
        
            
           
        
