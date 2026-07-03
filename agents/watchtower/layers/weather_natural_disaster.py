import aiohttp
import asyncio
import os
from datetime import datetime
import json
import feedparser

class WeatherNaturalDisasterLayer:
    """Layer 6 & 9: Weather and Natural Disaster Intelligence"""
    
    def __init__(self):
        self.usgs_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
        self.noaa_rss = "https://www.nhc.noaa.gov/index-at.xml"
        
    async def fetch_earthquakes(self, session: aiohttp.ClientSession) -> dict:
        """Fetch earthquakes > 4.5 magnitude in the last day"""
        try:
            async with session.get(self.usgs_url) as response:
                if response.status == 200:
                    data = await response.json()
                    events = []
                    for feature in data.get('features', [])[:5]:
                        props = feature['properties']
                        events.append({
                            "place": props['place'],
                            "magnitude": props['mag'],
                            "time": datetime.fromtimestamp(props['time'] / 1000).isoformat(),
                            "url": props['url']
                        })
                    return {"source": "USGS", "status": "success", "events": events}
                else:
                    return {"source": "USGS", "status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            return {"source": "USGS", "status": "error", "message": str(e)}

    async def fetch_hurricanes(self) -> dict:
        """Fetch active Atlantic hurricanes/cyclones from NOAA RSS"""
        try:
            # feedparser is blocking, but it's fast enough or we could run in executor
            loop = asyncio.get_running_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, self.noaa_rss)
            
            active_storms = []
            for entry in feed.entries:
                if "Summary" in entry.title or "Advisory" in entry.title:
                    active_storms.append({
                        "title": entry.title,
                        "summary": entry.summary[:200] + "...",
                        "link": entry.link
                    })
                    
            return {"source": "NOAA", "status": "success", "storms": active_storms[:3]}
        except Exception as e:
            return {"source": "NOAA", "status": "error", "message": str(e)}

    async def fetch_openweather(self, session: aiohttp.ClientSession) -> dict:
        """Fetch real-time weather at critical maritime chokepoints."""
        owm_key = os.getenv("OPENWEATHER_API_KEY")
        if not owm_key:
            return {"source": "OpenWeather", "status": "auth_error", "message": "OPENWEATHER_API_KEY not set"}
            
        # Query MULTIPLE strategic chokepoints for comprehensive coverage
        chokepoints = [
            {"name": "Red Sea / Bab el-Mandeb", "lat": 12.65, "lon": 43.35},
            {"name": "Strait of Hormuz", "lat": 27.18, "lon": 56.28},
            {"name": "Suez Canal", "lat": 30.45, "lon": 32.35},
            {"name": "Strait of Malacca", "lat": 2.50, "lon": 101.80},
        ]
        
        results = []
        for cp in chokepoints:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={cp['lat']}&lon={cp['lon']}&appid={owm_key}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather = data.get("weather", [{}])[0].get("main", "Clear")
                        desc = data.get("weather", [{}])[0].get("description", "")
                        wind = data.get("wind", {}).get("speed", 0)
                        temp_k = data.get("main", {}).get("temp", 0)
                        temp_c = round(temp_k - 273.15, 1) if temp_k > 0 else 0
                        results.append({
                            "chokepoint": cp["name"],
                            "condition": weather,
                            "description": desc,
                            "wind_speed_m_s": wind,
                            "temp_celsius": temp_c
                        })
            except Exception as e:
                results.append({"chokepoint": cp["name"], "condition": "Data Unavailable", "error": str(e)})
        
        if results:
            return {
                "source": "OpenWeather", 
                "status": "success",
                "chokepoint": results[0]["chokepoint"],  # Primary display
                "condition": results[0]["condition"],
                "wind_speed_m_s": results[0].get("wind_speed_m_s", 0),
                "all_chokepoints": results
            }
        return {"source": "OpenWeather", "status": "error", "message": "No chokepoint data retrieved"}

    async def fetch_all(self, session: aiohttp.ClientSession) -> dict:
        """Fetch all weather/disaster intelligence asynchronously"""
        print("Fetching Weather & Natural Disaster Intelligence (USGS, NOAA, OpenWeather)...")
        results = await asyncio.gather(
            self.fetch_earthquakes(session),
            self.fetch_hurricanes(),
            self.fetch_openweather(session)
        )
        return {
            "earthquakes": results[0],
            "hurricanes": results[1],
            "openweather": results[2]
        }
