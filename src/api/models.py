from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class ResearchQuery (BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="The research question")
    num_results: Optional[int] = Field(default=5, ge=1, le=100, description="Number of results to return")
    stream: Optional[bool] = Field(default=True, description="Enable streaming mode for real-time updates")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the latest advancements in AI?",
                "num_results": 5,
                "stream": True
            }
        }

class Source(BaseModel):
    title: str 
    url: str 
    highlight: Optional[List[str]] 
    published_date: Optional[str] = None
    author: Optional[str] = None 

class ResearchResponse(BaseModel):
    query: str = Field(..., description="The original research query")
    answer: str = Field(..., description="The synthesized answer to the query")
    sources: Optional[List[Source]] = Field(default=None, description="List of sources used in the research")
    research_time_taken: Optional[float] = Field(default=None, description="Time taken for the research in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the response generation")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the latest advancements in AI?",
                "answer": "Recent advancements include...",
                "sources": [
                    {
                        "title": "AI Research Journal",
                        "url": "https://example.com/ai-research",
                        "highlight": ["Key finding 1", "Key finding 2"],
                        "published_date": "2023-10-01",
                        "author": "John Doe"
                    }
                ],
                "research_time_taken": 2.5
            }
        }

