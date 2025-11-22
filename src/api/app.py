import os
import time 
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .research_service import ResearchService

load_dotenv()

research_service: ResearchService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global research_service
    try:
        research_service = ResearchService()
        await research_service.initialize()
    except Exception as e:
        raise e
    yield

    if research_service:
        await research_service.shutdown()

app = FastAPI(
    title="Multi Agent Research Assistant API",
    description="Ultra-fast AI-powered research assistant using Cerebras, Exa, and llamaindex.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Multi Agent Research Assistant",
        "heading": "Multi Agent Research Assistant",
        "description": "Ultra-fast AI-powered research assistant using Cerebras, Exa, and Llamaindex.",
        "badges": [
            "450 tokens/sec",
            "Semantic Search",
            "Multi-Agent workflows",
        ],
        "placeholder": "What are the latest development in quantum computing?",
        "examples": [
            "What are the latest development in quantum computing?",
            "Compare the performance of GPT-5 and Cerebras models.",
            "Explain the impact of blockchain technology on finance.",
        ],
        "footer_text": "Powered by Cerebras (inference), Exa (search), and Llamaindex (orchestration)."
    })


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    services = {}

    if research_service and research_service.initialized:
        services["research_service"] = "healthy"
    else:
        services["research_service"] = "unhealthy"

    services["cerebras_api_key"] = "configured" if os.getenv("CEREBRAS_API_KEY") else "missing"
    services["exa_api_key"] = "configured" if os.getenv("EXA_API_KEY") else "missing"

    overall_status = "healthy" if all(
        status == "healthy" for status in services.values()
    ) else "degraded"

    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        services=services
    )


@app.post("/api/research", response_model=ResearchResponse)
async def research_query(query: ResearchQuery):  
    if not research_service or not research_service.initialized:
        raise HTTPException(status_code=503, detail="Research service not initialized. Check API Configuration.")

    try:
        start_time = time.time()

        result = await research_service.execute_query(
            query=query.query,
            num_results=query.num_results,
        )

        research_time = time.time() - start_time

        sources = []
        if "sources" in result:
            for src in result["sources"]:
                sources.append(Source(
                    title=src.get("title", ""),
                    url=src.get("url", ""),
                    highlight=src.get("highlight", ""),
                    published_date=src.get("published_date"),
                    author=src.get("author"),
                ))

        return ResearchResponse(
            query=query.query,
            answer=result.get("answer", ""),
            source=source,                      
            research_time_taken=round(research_time, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        query = data.get("query", "")
        num_results = data.get("num_results", 5)

        if not query:
            await websocket.send_json({
                "type": "error",
                "content": "Query is required",
                "timestamp": time.time()
            })
            await websocket.close()
            return
        
        await websocket.send_json({
            "type":"start",
            "content": f"Starting research for: {query}",
            "timestamp": time.time()
        })

    async for chunk in research_service.execute_query_streaming   
        
