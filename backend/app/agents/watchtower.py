import math
from datetime import datetime

class DisruptionProbabilityEngine:
    SIGNAL_WEIGHTS = {
        'news_severity': 0.40,
        'price_anomaly': 0.25,
        'signal_count': 0.20,
        'trend_momentum': 0.15
    }

    def __init__(self):
        self.dpi_history = {} 

    def calculate_dpi(self, issue_query, signals, price_anomaly=None):
        # 1. News Component (aggregate all signals related to this issue)
        news_comp = self._calculate_news_component(signals)
        
        # 2. Price Component (Brent Crude anomaly)
        price_comp = self._calculate_price_component(price_anomaly)
        
        # 3. Signal Density
        density_comp = self._calculate_signal_density(signals)
        
        # 4. Trend Momentum
        trend_comp, trend_str = self._calculate_trend(issue_query)
        
        # 5. Weighted Average
        probability = (
            news_comp * self.SIGNAL_WEIGHTS['news_severity'] +
            price_comp * self.SIGNAL_WEIGHTS['price_anomaly'] +
            density_comp * self.SIGNAL_WEIGHTS['signal_count'] +
            trend_comp * self.SIGNAL_WEIGHTS['trend_momentum']
        )
        
        # 6. Sigmoid smoothing
        smoothed = self._sigmoid_scale(probability)
        
        # 7. Alert Level
        alert_level = self._determine_alert_level(smoothed)
        
        # 8. Confidence
        confidence = self._calculate_confidence(signals, price_anomaly)
        
        # Store for trend calculation
        if issue_query not in self.dpi_history:
            self.dpi_history[issue_query] = []
        self.dpi_history[issue_query].append(smoothed)
        if len(self.dpi_history[issue_query]) > 5:
            self.dpi_history[issue_query].pop(0)
            
        # Determine primary impacted region
        primary_region = "Global/Unknown"
        if signals:
            regions = [s.get('impacted_region', '') for s in signals if s.get('impacted_region')]
            if regions:
                primary_region = max(set(regions), key=regions.count)

        return {
            "issue": issue_query,
            "impacted_region": primary_region,
            "probability_30d": round(smoothed * 100, 2),
            "trend": trend_str,
            "alert_level": alert_level,
            "confidence": round(confidence * 100, 2),
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_news_component(self, signals):
        if not signals: return 0.0
        weights = [(s.get('severity', 1)/10.0) * s.get('confidence', 0.5) for s in signals]
        return min(1.0, max(weights) + (len(weights) * 0.05))

    def _calculate_price_component(self, price_anomaly):
        if not price_anomaly or not price_anomaly.get('is_anomaly') or price_anomaly.get('direction') == 'down':
            return 0.0
        z = price_anomaly.get('z_score', 0)
        if z >= 3.0: return 0.8
        if z >= 2.5: return 0.6
        if z >= 2.0: return 0.4
        return 0.0

    def _calculate_signal_density(self, signals):
        count = len(signals)
        if count >= 8: return 0.8
        if count >= 4: return 0.6
        if count >= 2: return 0.4
        if count >= 1: return 0.2
        return 0.0

    def _calculate_trend(self, issue_query):
        history = self.dpi_history.get(issue_query, [])
        if len(history) < 2: return 0.5, "stable"
        slope = history[-1] - history[0]
        if slope > 0.1: return 0.8, "increasing"
        if slope > 0.05: return 0.6, "increasing"
        if slope < -0.05: return 0.2, "decreasing"
        return 0.4, "stable"

    def _sigmoid_scale(self, x):
        return 1 / (1 + math.exp(-5 * (x - 0.5)))

    def _determine_alert_level(self, probability):
        if probability >= 0.80: return "critical"
        if probability >= 0.60: return "high"
        if probability >= 0.40: return "elevated"
        if probability >= 0.20: return "normal"
        return "low"

    def _calculate_confidence(self, signals, price_anomaly):
        if not signals: return 0.5
        avg_conf = sum(s.get('confidence', 0.5) for s in signals) / len(signals)
        boost = 0.1 if price_anomaly and price_anomaly.get('is_anomaly') else 0.0
        boost += 0.1 if len(signals) > 2 else 0.0
        return min(1.0, avg_conf + boost)


class WatchtowerAgent:
    def __init__(self, news_service, price_service, dpi_engine):
        self.news = news_service
        self.prices = price_service
        self.dpi = dpi_engine
        
    async def run_cycle(self, issue_query: str):
        print(f"--- WATCHTOWER AGENT: MONITORING ISSUE '{issue_query}' ---")
        
        # 1. Fetch News specific to this issue
        articles = await self.news.fetch_all_news(issue_query)
        
        # 2. Extract Signals specific to this issue
        signals = await self.news.extract_risk_signals(articles, issue_query)
        
        # 3. Detect Global Price Anomalies (Brent crude)
        price_anomaly = await self.prices.detect_anomaly("BZ=F") 
        
        # 4. Calculate DPI for this specific issue
        dpi_result = self.dpi.calculate_dpi(issue_query, signals, price_anomaly)
        
        if dpi_result['probability_30d'] >= 70.0:
            print(f"!!! CRITICAL ALERT: '{issue_query}' DPI at {dpi_result['probability_30d']}% !!!")
                
        return {
            "signals": signals,
            "price_anomaly": price_anomaly,
            "dpi_assessment": dpi_result
        }
