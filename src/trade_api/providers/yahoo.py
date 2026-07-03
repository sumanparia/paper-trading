import yfinance as yf
import pandas as pd
from typing import List, Dict
from trade_api.models import LiveQuote, HistoricalCandle
from trade_api.providers.base import DataProvider

class YahooProvider(DataProvider):
    async def fetch_live_quotes(self, symbols: List[str]) -> Dict[str, LiveQuote]:
        tickers = yf.Tickers(" ".join(symbols))
        result = {}
        for symbol in symbols:
            try:
                t = tickers.tickers[symbol]
                info = t.info
                result[symbol] = LiveQuote(
                    instrument_id=symbol,
                    symbol=symbol,
                    ltp=info.get("regularMarketPrice", 0.0),
                    open=info.get("regularMarketOpen", 0.0),
                    high=info.get("regularMarketDayHigh", 0.0),
                    low=info.get("regularMarketDayLow", 0.0),
                    close=info.get("regularMarketPreviousClose", 0.0),
                    volume=info.get("regularMarketVolume", 0)
                )
            except Exception as e:
                print(f"[Yahoo] Error fetching {symbol}: {e}")
        return result

    async def fetch_historical_data(self, symbol: str, interval: str, start: int, end: int) -> List[HistoricalCandle]:
        import pandas as pd
        
        # Translate Groww interval format to Yahoo Finance format
        yahoo_interval = interval
        if interval == "1m": yahoo_interval = "1m"
        elif interval == "3m": yahoo_interval = "3m"
        elif interval == "5m": yahoo_interval = "5m"
        elif interval == "15m": yahoo_interval = "15m"
        elif interval == "30m": yahoo_interval = "30m"
        elif interval == "1h": yahoo_interval = "60m" # Yahoo uses 60m for 1 hour
        elif interval == "1d": yahoo_interval = "1d"
        elif interval == "1w": yahoo_interval = "1wk"
        elif interval == "1mo": yahoo_interval = "1mo"
        else: yahoo_interval = "1d" # Fallback

        # Fetch data from Yahoo
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            interval=yahoo_interval, 
            start=pd.to_datetime(start, unit='s'), 
            end=pd.to_datetime(end, unit='s'),
            prepost=False # Don't include pre/post market hours unless requested
        )
        
        candles = []
        for timestamp, row in df.iterrows():
            # Skip rows with no volume (sometimes Yahoo returns empty rows for intervals)
            if row['Volume'] == 0 and interval != "1d":
                continue
                
            candles.append(HistoricalCandle(
                timestamp=int(timestamp.timestamp()),
                open=round(row['Open'], 2),
                high=round(row['High'], 2),
                low=round(row['Low'], 2),
                close=round(row['Close'], 2),
                volume=int(row['Volume'])
            ))
            
        # Groww returns data in ascending order (oldest first)
        candles.sort(key=lambda x: x.timestamp)
        return candles
