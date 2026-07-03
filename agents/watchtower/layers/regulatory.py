import aiohttp
import asyncio
from datetime import datetime, timedelta

class RegulatoryLayer:
    """Layer 7: Regulatory & Legal Intelligence"""
    
    def __init__(self):
        self.fed_reg_url = "https://www.federalregister.gov/api/v1/documents.json"
        
    async def fetch_federal_register(self, session: aiohttp.ClientSession) -> dict:
        """Fetch recent documents related to sanctions or energy policy"""
        try:
            # Look back 7 days
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            params = {
                "conditions[term]": "sanctions OR petroleum OR pipeline OR embargo",
                "conditions[publication_date][gte]": start_date,
                "per_page": 5,
                "order": "newest"
            }
            
            async with session.get(self.fed_reg_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    docs = []
                    for doc in data.get('results', []):
                        docs.append({
                            "title": doc.get('title'),
                            "type": doc.get('type'),
                            "agency": doc.get('agencies', [{}])[0].get('name', 'Unknown'),
                            "publication_date": doc.get('publication_date'),
                            "url": doc.get('html_url')
                        })
                    return {"source": "Federal Register", "status": "success", "documents": docs}
                else:
                    return {"source": "Federal Register", "status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            return {"source": "Federal Register", "status": "error", "message": str(e)}

    async def fetch_all(self, session: aiohttp.ClientSession) -> dict:
        """Fetch all regulatory intelligence asynchronously"""
        print("Fetching Regulatory & Legal Intelligence...")
        results = await asyncio.gather(
            self.fetch_federal_register(session)
        )
        return {
            "federal_register": results[0]
        }
