import aiohttp
import asyncio
import feedparser
from datetime import datetime, timedelta

class TradeAcademicLayer:
    """Layers 8, 9, 10: Trade, Academic, and Leaks Intelligence"""
    
    def __init__(self):
        # UN Comtrade public API (No key needed for basic)
        self.comtrade_url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
        # arXiv API
        self.arxiv_url = "http://export.arxiv.org/api/query"

    async def fetch_comtrade(self, session: aiohttp.ClientSession) -> dict:
        """Fetch UN Comtrade oil/gas export data changes (Simulated recent pull)"""
        try:
            # UN Comtrade can be slow/rate limited. For hackathon, we fetch public data.
            # Petroleum oils = HS code 2709
            params = {
                "reporterCode": "all",
                "partnerCode": "0", # World
                "cmdCode": "2709",
                "flowCode": "M,X",
                "period": (datetime.now() - timedelta(days=60)).strftime("%Y%m") # 2 months ago (latest available usually)
            }
            # Note: The real API often requires complex auth for live data. 
            # We'll make a public call and handle rate limits gracefully.
            async with session.get(self.comtrade_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"source": "UN Comtrade", "status": "success", "total_records": len(data.get('data', []))}
                else:
                    return {"source": "UN Comtrade", "status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            return {"source": "UN Comtrade", "status": "error", "message": str(e)}

    async def fetch_arxiv(self, session: aiohttp.ClientSession) -> dict:
        """Fetch latest academic papers on energy security/vulnerabilities."""
        try:
            query = "all:\"energy infrastructure\" OR all:\"pipeline vulnerability\""
            params = {
                "search_query": query,
                "start": 0,
                "max_results": 3,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
            async with session.get(self.arxiv_url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    loop = asyncio.get_running_loop()
                    feed = await loop.run_in_executor(None, feedparser.parse, text)
                    papers = [{"title": entry.title, "summary": entry.summary[:100]} for entry in feed.entries]
                    return {"source": "arXiv", "status": "success", "papers": papers}
                else:
                    return {"source": "arXiv", "status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            return {"source": "arXiv", "status": "error", "message": str(e)}

    async def fetch_leaks(self) -> dict:
        """Monitor open leak aggregators/forums (Concept for Hackathon)"""
        return {"source": "Leak Aggregators", "status": "success", "leaks_detected": False}

    async def fetch_all(self, session: aiohttp.ClientSession) -> dict:
        print("Fetching Trade & Academic Intelligence...")
        results = await asyncio.gather(
            self.fetch_comtrade(session),
            self.fetch_arxiv(session),
            self.fetch_leaks()
        )
        return {
            "un_comtrade": results[0],
            "arxiv": results[1],
            "leaks": results[2]
        }
