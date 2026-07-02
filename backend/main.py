from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.app.agents.parser import CrisisParserAgent
from backend.app.services.news_service import NewsService
from backend.app.services.price_service import PriceService
from backend.app.agents.watchtower import DisruptionProbabilityEngine, WatchtowerAgent

app = FastAPI(title="Energy Resilience Command API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

parser_agent = CrisisParserAgent()
news_service = NewsService()
price_service = PriceService()
dpi_engine = DisruptionProbabilityEngine()
watchtower = WatchtowerAgent(news_service, price_service, dpi_engine)

app.mount("/static", StaticFiles(directory=os.path.join(ROOT_DIR, "frontend")), name="static")

from typing import Optional

class SimulateRequest(BaseModel):
    issue_query: Optional[str] = "Taiwan Blockade"

@app.get("/")
def read_root():
    return FileResponse(os.path.join(ROOT_DIR, "frontend", "index.html"))

@app.get("/favicon.ico")
def read_favicon():
    return {"status": "dummy"}

@app.post("/api/simulate")
async def run_simulation(req: Optional[SimulateRequest] = None):
    """Runs the full pipeline starting with the Parser."""
    
    query = req.issue_query if req and req.issue_query else "Taiwan Blockade"
    # Agent 0: Parse the user's natural language input
    crisis_params = await parser_agent.parse_crisis(query)
    
    # Agent 1: Watchtower uses the optimized search query from the parser
    search_query = crisis_params.get("search_query", query)
    wt_results = await watchtower.run_cycle(search_query)
    
    return {
        "crisis_params": crisis_params,
        "watchtower": wt_results
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
