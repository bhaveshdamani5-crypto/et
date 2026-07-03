import asyncio
import os
import yfinance as yf
from datetime import datetime

class FinancialLayer:
    """Layer 4: Financial Intelligence (Options Flow, Freight proxies)"""
    
    def __init__(self):
        # USO = United States Oil Fund (proxy for oil options flow)
        # BDRY = Breakwave Dry Bulk Shipping ETF (proxy for freight rates)
        self.tickers = ["USO", "BDRY", "XOM"]
        
    async def fetch_options_flow(self, ticker_symbol: str) -> dict:
        """Fetch put/call ratio or unusual volume proxy"""
        try:
            loop = asyncio.get_running_loop()
            ticker = yf.Ticker(ticker_symbol)
            
            # This can be slow, run in executor
            def _get_options_data():
                try:
                    expirations = ticker.options
                    if not expirations:
                        return None
                    
                    # Get near-term expiration
                    opt = ticker.option_chain(expirations[0])
                    calls_vol = opt.calls['volume'].sum() if 'volume' in opt.calls else 0
                    puts_vol = opt.puts['volume'].sum() if 'volume' in opt.puts else 0
                    
                    put_call_ratio = puts_vol / calls_vol if calls_vol > 0 else 0
                    
                    return {
                        "expiration": str(expirations[0]),
                        "calls_volume": int(calls_vol) if not calls_vol != calls_vol else 0, # check for NaN
                        "puts_volume": int(puts_vol) if not puts_vol != puts_vol else 0,
                        "put_call_ratio": float(round(put_call_ratio, 2)),
                        "anomalous": bool(put_call_ratio > 1.5)
                    }
                except Exception as e:
                    return str(e)

            result = await loop.run_in_executor(None, _get_options_data)
            
            if isinstance(result, str):
                return {"status": "error", "message": result}
            elif result:
                return {"status": "success", "data": result}
            return {"status": "error", "message": "No options data"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def fetch_price_trends(self) -> dict:
        """Fetch recent price movements to detect spikes"""
        try:
            loop = asyncio.get_running_loop()
            def _get_prices():
                data = yf.download(self.tickers, period="5d", progress=False)['Close']
                trends = {}
                for t in self.tickers:
                    if t in data:
                        series = data[t].dropna()
                        if len(series) >= 2:
                            change_pct = float(((series.iloc[-1] - series.iloc[-2]) / series.iloc[-2]) * 100)
                            trends[t] = {
                                "current_price": float(round(series.iloc[-1], 2)),
                                "change_pct": float(round(change_pct, 2))
                            }
                return trends
                
            trends = await loop.run_in_executor(None, _get_prices)
            return {"status": "success", "trends": trends}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def fetch_crypto_flows(self, session) -> dict:
        """Layer 10: Crypto & Stablecoin Flows (Etherscan)"""
        etherscan_key = os.getenv("ETHERSCAN_API_KEY")
        if not etherscan_key:
            return {"source": "Etherscan", "status": "auth_error", "message": "ETHERSCAN_API_KEY not set"}
            
        try:
            # Check Tether (USDT) large transfers on Ethereum as a proxy for capital flight
            url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress=0xdac17f958d2ee523a2206206994597c13d831ec7&page=1&offset=5&sort=desc&apikey={etherscan_key}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    transfers = data.get("result", [])
                    return {"source": "Crypto Flows", "status": "success", "latest_large_transfers": len(transfers)}
                return {"source": "Crypto Flows", "status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            return {"source": "Crypto Flows", "status": "error", "message": str(e)}

    async def fetch_all(self, session) -> dict:
        """Fetch all financial intelligence asynchronously"""
        print("Fetching Financial Intelligence (Options, Freight, Crypto)...")
        results = await asyncio.gather(
            self.fetch_options_flow("USO"),
            self.fetch_price_trends(),
            self.fetch_crypto_flows(session)
        )
        return {
            "oil_options_flow": results[0],
            "price_trends": results[1],
            "crypto_flows": results[2]
        }
