import os
import json
import urllib.parse
import feedparser
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class NewsService:
    def __init__(self):
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY")
        if self.nvidia_api_key:
            self.llm = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.nvidia_api_key,
                timeout=15.0
            )
        else:
            self.llm = None
            print("WARNING: No NVIDIA_API_KEY found.")

    async def fetch_all_news(self, issue_query: str, hours_back: int = 24) -> list:
        """Fetches news specifically related to the dynamic global issue."""
        import requests
        articles = []
        
        # We now search for the EXACT issue query without forcing "oil or energy" keywords
        search_term = issue_query
        encoded_query = urllib.parse.quote(search_term)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        print(f"Fetching global news for issue: {issue_query}")
        try:
            # Use requests with a timeout to prevent hanging
            rss_text = requests.get(rss_url, timeout=5.0).text
            feed = feedparser.parse(rss_text)
            for entry in feed.entries[:5]: # Ultra-fast: process only the top 5 most relevant articles
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", ""),
                    "source": rss_url,
                    "published_at": entry.get("published", datetime.now().isoformat())
                })
        except Exception as e:
            print(f"Error fetching Google News: {e}")
            
        print(f"Fetched {len(articles)} articles related to '{issue_query}'.")
        return articles

    async def extract_risk_signals(self, articles: list, issue_query: str) -> list:
        """Uses LLM to extract structured risk signals tailored to the user's issue in ONE fast batch call."""
        if not self.llm or not articles:
            print("No LLM client or no articles. Skipping extraction.")
            return []
            
        signals = []
        print(f"Extracting risk signals from {len(articles)} articles in a single batched call for maximum speed...")
        
        # Combine all articles into a single text block
        articles_text = ""
        for i, article in enumerate(articles):
            articles_text += f"\n--- ARTICLE {i+1} ---\nTitle: {article['title']}\nDescription: {article['description']}\n"
            
        prompt = f"""
        You are an elite geopolitical risk analyst.
        The user is investigating the following global issue: "{issue_query}"

        Analyze the following news articles and extract structured risk signals related to the issue.
        {articles_text}

        CRITICAL INSTRUCTIONS:
        1. DO NOT output repetitive signals. If multiple articles talk about the same event, CONSOLIDATE them into a SINGLE signal with higher confidence.
        2. Provide deep, specific analysis in the description, not just generic summaries. Name specific entities, dates, and locations.
        3. Do not just default to 6/10 severity or 80% confidence. Use the full scale.
        4. Return a MAXIMUM of 3 highly distinct, unique signals.

        Return them as a JSON ARRAY of objects. Format EXACTLY like this:
        [
            {{
                "event_type": "<select one>",
                "impacted_region": "<specific country, region, or affected area>",
                "severity": <integer 1-10>,
                "confidence": <float 0.0-1.0>,
                "description": "<detailed, highly specific analysis of the threat>"
            }}
        ]

        EVENT TYPE OPTIONS:
        military_conflict, geopolitical_tension, trade_disruption, infrastructure_attack, sanctions, natural_disaster, labor_dispute, accident, diplomatic, economic

        SEVERITY SCALE:
        10: Full-scale war, complete blockade
        8: Significant military action, severe disruption
        6: Major diplomatic crisis
        4: Minor incident, protests
        2: Routine concern

        Return ONLY a valid JSON array (`[]`). No markdown.
        """
        
        try:
            completion = self.llm.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1024
            )
            
            content = completion.choices[0].message.content
            content = content.replace("```json", "").replace("```", "").strip()
            
            # The LLM should return a JSON array
            extracted_signals = json.loads(content)
            
            if isinstance(extracted_signals, list):
                for signal in extracted_signals:
                    if int(signal.get("severity", 0)) >= 2:
                        signal["timestamp"] = datetime.now().isoformat()
                        signals.append(signal)
                        
        except Exception as e:
            print(f"Extraction error: {e}")
            
        return signals
