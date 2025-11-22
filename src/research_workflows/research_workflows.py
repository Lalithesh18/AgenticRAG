#event driven architecture

from typing import Dict,Any,List
from llama_index.core.workflow import(
    workflow,
    StartEvent,
    StopEvent,
    step,
    Event,
    Context
)

from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage

class ResearchEvent(Event):
    query:str

class AnalysisEvent(Event):
    research_data:str
    original_query: str

class ResearchWorkflow(workflow):

    def __init__(
        self,
        research_agent:ReActAgent,
        analysis_agent:ReActAgent,
        verbose:bool=True,
        **kwargs
    ):
        super().__init__(**kwargs)   #Fetching research agent, analysis agent and verbosity from the parent class
        self.research_agent = research_agent
        self.analysis_agent = analysis_agent
        self.verbose = verbose
        
    @step
    async def start(self,ctx: Context,ev:StartEvent)->ResearchEvent:
        query = ev.get("query")

        if self.verbose:
            print(f"\nStarting Research Workflow...")
        
        await ctx.set("original query",query)

        return ResearchEvent(query=query)
    
    @step
    async def research_phase(self,ctx:Context,ev:ResearchEvent)->AnalysisEvent:

        if self.verbose:
            print("Research agent is active...")
        
        research_task = (
            f"Research the following query and gather comphrensive information:{ev.query}\n\n"
            "use the search_web tool to find relevant sources."
            "if needed, use get_content to fetch detailes information from specific URLs."
            "Provide a summary of all sources found with their URLs."
        )

        response = await self.research_agent.achat(research_task)

        research_data = str(response)

        if self.verbose:
            print(f"\n Research Complete. Data collected.")
        
        return AnalysisEvent(
            research_data = research_data,
            original_query=ev.query
        )
    
    @step
    async def analysis_phase(self,ctx:Context, ev:AnalysisEvent)-> StopEvent:

        if self.verbose:
            print("Analysis agent active...")
        
        analysis_task = (
            f"Analysis the following research data and answer user's question.\n\n"
            f"Original question:{ev.original_query}\n\n"
            f"Research Data: {ev.research_data} \n\n"
            "Provide a comprehensive answer that:\n"
            "1.Directly addresses the user's question.\n"
            "2.Synthesis key findings from the research\n"
            "3.Includes relevant citations and sources.\n"
            "4. Present information in a clear, structured format\n"
        )

        response = await self.analysis_agent.achat(analysis_task)

        final_answer = str(response)

        if self.verbose:
            print("Workflow Complete.")

        return StopEvent(result=final_answer)
    
async def run_search_query(
        workflow: ResearchWorkflow,
        query: str
)->str:
    result = await workflow.run(query=query)
    return result

    
        