import os
import json
import feedparser
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

class RiskSignal(BaseModel):
    corridor: str = Field(description="The geographic corridor affected (e.g., 'Hormuz', 'Red Sea', 'US Gulf')")
    disruption_probability: float = Field(description="Probability of disruption (0.0 to 1.0)")
    confidence: float = Field(description="Confidence in this assessment (0.0 to 1.0)")
    urgency: float = Field(description="Urgency of the situation (0.0 to 1.0)")
    reasoning: str = Field(description="Brief reasoning for the score")
    
class WatchtowerOutput(BaseModel):
    signals: List[RiskSignal]

class WatchtowerAgent:
    def __init__(self):
        # Free RSS feeds that are good for geopolitical news
        self.rss_feeds = [
            "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000811"
        ]
        
        if NVIDIA_API_KEY:
            self.client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=NVIDIA_API_KEY
            )
        else:
            self.client = None
            
    def fetch_news(self) -> List[dict]:
        """Fetch news from RSS feeds and filter for relevant keywords."""
        keywords = ["oil", "tanker", "ship", "strait", "hormuz", "red sea", "iran", "saudi", "houthi", "suez", "attack", "disruption"]
        relevant_news = []
        
        print("Fetching news from RSS feeds...")
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]: # Top 10 from each feed
                    title = entry.get("title", "").lower()
                    summary = entry.get("summary", "").lower()
                    
                    if any(kw in title or kw in summary for kw in keywords):
                        relevant_news.append({
                            "title": entry.get("title"),
                            "link": entry.get("link"),
                            "published": entry.get("published")
                        })
            except Exception as e:
                print(f"Error fetching feed {feed_url}: {e}")
                
        return relevant_news

    def extract_signals_mock(self, news_items: List[dict]) -> WatchtowerOutput:
        """Mock LLM extraction for testing without an API key."""
        if not news_items:
            return WatchtowerOutput(signals=[
                RiskSignal(
                    corridor="Hormuz", 
                    disruption_probability=0.1, 
                    confidence=0.8,
                    urgency=0.1,
                    reasoning="No significant geopolitical news detected."
                )
            ])
            
        hormuz_mentions = sum(1 for item in news_items if "hormuz" in item["title"].lower() or "iran" in item["title"].lower())
        red_sea_mentions = sum(1 for item in news_items if "red sea" in item["title"].lower() or "houthi" in item["title"].lower())
        
        signals = []
        if hormuz_mentions > 0:
            signals.append(RiskSignal(
                corridor="Hormuz",
                disruption_probability=min(0.2 + (hormuz_mentions * 0.15), 0.95),
                confidence=0.75,
                urgency=min(0.2 + (hormuz_mentions * 0.2), 0.9),
                reasoning=f"Detected {hormuz_mentions} news items indicating tension in the Hormuz region."
            ))
        if red_sea_mentions > 0:
            signals.append(RiskSignal(
                corridor="Red Sea",
                disruption_probability=min(0.3 + (red_sea_mentions * 0.1), 0.9),
                confidence=0.8,
                urgency=min(0.3 + (red_sea_mentions * 0.15), 0.85),
                reasoning=f"Detected {red_sea_mentions} news items indicating tension in the Red Sea."
            ))
            
        if not signals:
            signals.append(RiskSignal(
                corridor="Global", 
                disruption_probability=0.2, 
                confidence=0.6,
                urgency=0.2,
                reasoning="General energy news detected, no specific corridor threats."
            ))
            
        return WatchtowerOutput(signals=signals)

    def extract_signals_nvidia(self, news_items: List[dict]) -> WatchtowerOutput:
        """Use NVIDIA NIM API to extract risk signals."""
        if not self.client:
            print("No NVIDIA_API_KEY found, falling back to mock extraction.")
            return self.extract_signals_mock(news_items)
            
        headlines = "\\n".join([f"- {item['title']}" for item in news_items])
        
        prompt = f'''
        You are a Geopolitical Risk Intelligence Agent. Analyze the following recent news headlines
        and assess the disruption probability for major oil shipping corridors (Hormuz, Red Sea, US Gulf).
        
        Headlines:
        {headlines}
        
        Output a JSON object with a list of 'signals'. Each signal must have:
        - corridor (string)
        - disruption_probability (float 0.0-1.0)
        - confidence (float 0.0-1.0)
        - urgency (float 0.0-1.0)
        - reasoning (string)
        
        Respond with ONLY the valid JSON object. Do not include markdown formatting, backticks, or extra text.
        '''
        
        try:
            print("Analyzing headlines via NVIDIA NIM (Llama 3.1 70B)...")
            completion = self.client.chat.completions.create(
                model="meta/llama-3.1-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=1024,
            )
            content = completion.choices[0].message.content
            # Clean up markdown formatting if the LLM adds it
            content = content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(content)
            
            signals = [RiskSignal(**s) for s in parsed.get("signals", [])]
            return WatchtowerOutput(signals=signals)
            
        except Exception as e:
            print(f"Error calling NVIDIA API: {e}")
            print("Falling back to mock extraction.")
            return self.extract_signals_mock(news_items)

    def run(self) -> WatchtowerOutput:
        """Main execution flow for Watchtower agent."""
        print("--- WATCHTOWER AGENT ACTIVATED ---")
        news = self.fetch_news()
        print(f"Found {len(news)} relevant news items.")
        
        for item in news:
            print(f"  -> {item['title']}")
            
        if self.client:
            result = self.extract_signals_nvidia(news)
        else:
            result = self.extract_signals_mock(news)
            
        return result

if __name__ == "__main__":
    agent = WatchtowerAgent()
    output = agent.run()
    
    print("\n--- WATCHTOWER OUTPUT ---")
    print(output.model_dump_json(indent=2))
