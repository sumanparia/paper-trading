import httpx
from trade_api.config import settings
from trade_api.models import LiveQuote, HistoricalCandle
from trade_api.providers.base import DataProvider
from typing import List, Dict
from datetime import datetime

class FinnhubProvider(DataProvider):
    
    async def fetch_live_quotes(self, symbols: List[str]) -> Dict[str, LiveQuote]:
        async with httpx.AsyncClient() as client:
            result = {}
            for symbol in symbols:
                try:
                    resp = await client.get(
                        f"https://finnhub.io/api/v1/quote", 
                        params={"symbol": symbol, "token": settings.finnhub_api_key}
                    )
                    data = resp.json()
                    result[symbol] = LiveQuote(
                        instrument_id=symbol,
                        symbol=symbol,
                        ltp=data.get("c", 0.0),
                        open=data.get("o", 0.0),
                        high=data.get("h", 0.0),
                        low=data.get("l", 0.0),
                        close=data.get("pc", 0.0),
                        volume=data.get("v", 0)
                    )
                except Exception as e:
                    print(f"[Finnhub] Error fetching live quote {symbol}: {e}")
            return result

    async def fetch_historical_data(self, symbol: str, interval: str, start: int, end: int) -> List[HistoricalCandle]:
        """
        Fetches historical candles from Finnhub.
        Note: Finnhub requires 't' (from) and 'to' in SECONDS.
        """
        # Map Groww standard intervals to Finnhub resolution strings
        finnhub_resolution = "D" # Default to Daily
        if interval in ["1m", "3m", "5m"]: finnhub_resolution = "5"  # Finnhub free tier min is 5m
        elif interval == "15m": finnhub_resolution = "15"
        elif interval == "30m": finnhub_resolution = "30"
        elif interval == "1h": finnhub_resolution = "60"
        elif interval in ["1d", "1D"]: finnhub_resolution = "D"
        elif interval in ["1w", "1W"]: finnhub_resolution = "W"
        elif interval in ["1mo", "1M"]: finnhub_resolution = "M"

        params = {
            "symbol": symbol,
            "resolution": finnhub_resolution,
            "from": start,
            "to": end,
            "token": settings.finnhub_api_key
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get("https://finnhub.io/api/v1/stock/candle", params=params)
                data = resp.json()
                
                # Finnhub returns an 's' (status) key. "ok" means success. "no_data" means your tier doesn't support it.
                if data.get("s") != "ok":
                    error_msg = data.get("s", "Unknown error")
                    print(f"[Finnhub] No historical data returned for {symbol}. Status: {error_msg}. (Check API tier limits)")
                    # Returning empty list allows the system to fail gracefully or try next provider in pool
                    return [] 

                candles = []
                # Finnhub returns parallel arrays: t (timestamps), o, h, l, c, v
                timestamps = data.get("t", [])
                opens = data.get("o", [])
                highs = data.get("h", [])
                lows = data.get("l", [])
                closes = data.get("c", [])
                volumes = data.get("v", [])

                for i in range(len(timestamps)):
                    candles.append(HistoricalCandle(
                        timestamp=timestamps[i],
                        open=round(opens[i], 2),
                        high=round(highs[i], 2),
                        low=round(lows[i], 2),
                        close=round(closes[i], 2),
                        volume=volumes[i]
                    ))
                
                # Finnhub already returns data in ascending order (oldest first)
                return candles

            except httpx.HTTPStatusError as e:
                print(f"[Finnhub] HTTP Error fetching history for {symbol}: {e.response.status_code}")
                return []
            except Exception as e:
                print(f"[Finnhub] Exception fetching history for {symbol}: {e}")
                return []