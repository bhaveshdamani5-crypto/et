import random
from datetime import datetime

class AISService:
    """Simulates real-time AIS shipping data for the hackathon prototype."""
    
    async def get_route_volume(self, issue_query: str) -> dict:
        """Returns AIS volume changes based on the geopolitical issue."""
        # For a hackathon, we simulate the drop in traffic realistically
        base_volume = random.randint(300, 500)
        
        # If the issue sounds severe, simulate a massive drop in AIS pings (rerouting)
        is_severe = any(word in issue_query.lower() for word in ['war', 'blockade', 'strike', 'missile', 'pirate'])
        drop_percent = random.uniform(30.0, 75.0) if is_severe else random.uniform(2.0, 10.0)
        
        current_volume = int(base_volume * (1 - (drop_percent / 100)))
        
        return {
            "corridor": issue_query,
            "baseline_daily_vessels": base_volume,
            "current_daily_vessels": current_volume,
            "volume_change_percent": round(-drop_percent, 1),
            "rerouting_detected": is_severe,
            "timestamp": datetime.now().isoformat()
        }

class SanctionsService:
    """Checks entities against OFAC/EU/UN Sanctions lists."""
    
    async def check_sanctions(self, issue_query: str) -> dict:
        """Simulates checking entities related to the crisis against OFAC lists."""
        # Simulate finding blocked entities
        is_sanction_risk = any(word in issue_query.lower() for word in ['russia', 'iran', 'venezuela', 'sanction', 'embargo'])
        hits = random.randint(3, 12) if is_sanction_risk else random.randint(0, 1)
        
        return {
            "query": issue_query,
            "ofac_hits": hits,
            "eu_hits": hits - 1 if hits > 0 else 0,
            "un_hits": hits - 2 if hits > 1 else 0,
            "total_sanctions_hits": hits + (hits - 1 if hits > 0 else 0) + (hits - 2 if hits > 1 else 0),
            "risk_level": "HIGH" if hits > 5 else ("MODERATE" if hits > 0 else "LOW"),
            "timestamp": datetime.now().isoformat()
        }

class SatelliteService:
    """Monitors satellite imagery (Sentinel-2/NASA) for port congestion and anomalies."""
    
    async def get_satellite_analysis(self, issue_query: str) -> dict:
        """Simulates NDVI/shadow analysis for port congestion and military activity."""
        is_conflict = any(word in issue_query.lower() for word in ['war', 'military', 'blockade', 'navy'])
        
        # Attempt to grab a real photo of the region from Wikipedia
        image_url = ""
        try:
            import urllib.parse
            import requests
            region = issue_query.split()[-1] if len(issue_query.split()) > 0 else "Earth"
            wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(region)}&prop=pageimages&format=json&pithumbsize=500"
            res = requests.get(wiki_url, timeout=3.0).json()
            pages = res.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if "thumbnail" in page_data:
                    image_url = page_data["thumbnail"]["source"]
                    break
        except Exception:
            pass
            
        return {
            "target_region": issue_query,
            "port_congestion_index": round(random.uniform(7.0, 9.5) if is_conflict else random.uniform(2.0, 5.0), 1),
            "abnormal_military_activity": is_conflict,
            "storage_tank_levels": f"{random.randint(40, 95)}% capacity",
            "confidence_score": 0.88,
            "image_url": image_url,
            "last_satellite_pass": datetime.now().isoformat()
        }
