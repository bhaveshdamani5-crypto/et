import numpy as np
import yfinance as yf
from datetime import datetime

class PriceService:
    def __init__(self):
        self.anomaly_threshold = 2.0
        
    async def fetch_current_prices(self) -> dict:
        prices = {}
        try:
            # BZ=F is Brent Crude, CL=F is WTI
            for ticker, name in [("BZ=F", "brent"), ("CL=F", "wti")]:
                ticker_obj = yf.Ticker(ticker)
                hist = ticker_obj.history(period="1d")
                if not hist.empty:
                    prices[name] = {
                        "price": round(float(hist['Close'].iloc[-1]), 2),
                        "currency": "USD",
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"Error fetching prices: {e}")
            prices = {
                "brent": {"price": 78.40, "currency": "USD", "timestamp": datetime.now().isoformat()}
            }
        return prices

    async def detect_anomaly(self, ticker="BZ=F") -> dict:
        try:
            ticker_obj = yf.Ticker(ticker)
            # Get 30 days of data for z-score calculation
            hist = ticker_obj.history(period="30d")
            
            if hist.empty or len(hist) < 5:
                return {"is_anomaly": False, "z_score": 0.0, "percent_change_24h": 0.0, "severity": "low", "current_price": 0.0}
                
            closes = hist['Close'].values
            current_price = closes[-1]
            previous_price = closes[-2] if len(closes) > 1 else current_price
            
            mean = np.mean(closes)
            std = np.std(closes)
            
            z_score = (current_price - mean) / std if std > 0 else 0
            percent_change_24h = ((current_price - previous_price) / previous_price) * 100
            
            is_anomaly = z_score >= self.anomaly_threshold
            
            severity = "low"
            if z_score >= 3.0:
                severity = "extreme"
            elif z_score >= 2.0:
                severity = "high"
            elif z_score >= 1.5:
                severity = "moderate"
                
            return {
                "is_anomaly": bool(is_anomaly),
                "z_score": round(float(z_score), 2),
                "percent_change_24h": round(float(percent_change_24h), 2),
                "severity": severity,
                "direction": "up" if z_score > 0 else "down",
                "current_price": round(float(current_price), 2)
            }
        except Exception as e:
            print(f"Error detecting anomaly: {e}")
            return {"is_anomaly": False, "z_score": 0.0, "percent_change_24h": 0.0, "severity": "low", "current_price": 0.0}
