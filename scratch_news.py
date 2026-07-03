import asyncio
import os
from backend.app.services.news_service import NewsService

async def main():
    service = NewsService()
    articles = await service.fetch_all_news("red sea oil crisis")
    print(f"Fetched {len(articles)} articles.")
    
    if articles:
        signals = await service.extract_risk_signals(articles, "red sea oil crisis")
        print(f"Extracted {len(signals)} signals.")
        for s in signals:
            print(s)
            
if __name__ == "__main__":
    asyncio.run(main())
