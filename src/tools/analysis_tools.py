from typing import List,Dict,Any
from llama_index.core.tools import FunctionTool

class AnalysisTools:

    def summarize_sources(self,sources:List[Dict[str,Any]]) -> Dict[str,Any]:

        if not sources:
            return{
                "summary":"No sources provided to summarize.",
                "num_sources":0,
                "key_points":[] 
            }
        
        key_points = []
        source_info = []

        for index, source in enumerate(source,1):
            title = source.get("title","unknown Title")
            url = source.get("url","")
            
            text = ""

            if "highlights" in source and source["highlights"]:
                text = " ".join(source["highlights"])
            elif "text" in source:
                text = source["text"][:500]

            source_info.append({
                "source_number":index,
                "title":title,
                "url":url,
                "preview":text[:200] + "..." if len(text) > 200 else text
            })

        return{
            "summary":f"I analyzed {len(sources)} sources on the research topic.",
            "num_source":len(sources),
            "sources": source_info,
            "note": "Use this information to generate insights and answer user's question."
        }
    
    def compare_information(self,data:List[Dict[str,Any]])->Dict[str,Any]:

        if not data or len(data) < 2:
            return{
                "comparison":"Need at least 2 items to compare",
                "num_items": len(data) if data else 0
            }
        items = []

        for index,item in enumerate(data,1):
            items.append({
                "item_number":index,
                "title":item.get("title",f"Item{index}"),
                "url":item.get("url",""),
                "key_info":item.get("text","")[:300] if "text" in item else ""
            })

        return{
            "comparison": f"Comapring {len(data)} items for analysis.",
            "num_items":len(data),
            "items": items,
            "note": "Review these items to identify similarities, difference and key insights."
        }

    def extract_key_insights(self,content:str,topic:str="")->Dict[str,Any]:
        if not content:
            return{
                "insights":"No content provided",
                "content_lenght":0
            }
            
            word_count = len(content.split())
            preview = content [:300] + "..." if len(content) >300 else content
            
            return{
               "topic":topic if topic else "general Anaysis",
               "content_lenght":word_count,
               "preview":preview,
               "note":"Analyse this content to extract relavent insights for the user's query" 
            }
            
def create_summerize_tool(analysis_tools:AnalysisTools) -> FunctionTool:
    
    return FunctionTool.from_defaults(
        fn = analysis_tools.summarize_sources,
        name="summarize_sources",
        description="""Summerize research sources into key insights.
        Use this to consolidate findings from multiple sources.
        Args:
             sources(List[Dict]): List of source dictionaries containing research data.
        Returns:
              Dictionary with structured summery of all sources.
        """
    )
    
def create_compare_tool(analysis_tools:AnalysisTools) -> FunctionTool:
    
    return FunctionTool.from_defaults(
        fn = analysis_tools.compare_information,
        name="compare_information",
        description="""Scompare and cross-reference information from multiple sources.
        Use this to identify similarities, differences, and patterns across sources.
        Args:
             sources(List[Dict]): List of data points or sources to compare
        Returns:
              Dictionary with analytics.
        """
    )
    
def create_insights_tool(analysis_tools:AnalysisTools) -> FunctionTool:
    
    return FunctionTool.from_defaults(
        fn = analysis_tools.extract_key_insigths,
        name="extract_key_insigths",
        description="""Extract key insights from content.
        Use this to identify importtant points from a piece of text.
        Args:
             content (str):The text Content to analyze.
             topic (str):Optional topic to focus the extraction on
        Returns:
              Dictionary with structured insights.
        """
    )