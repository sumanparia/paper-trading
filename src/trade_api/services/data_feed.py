import asyncio
from typing import Dict, List, Set
from trade_api.models import LiveQuote
from trade_api.providers.base import DataProvider
from trade_api.config import settings
from trade_api.services.order_monitor import order_monitor_service

class DataFeedService:
    def __init__(self, provider: DataProvider = None):
        self.provider = provider
        self._cache: Dict[str, LiveQuote] = {}
        self._subscribed_symbols: Set[str] = set()
        self._lock = asyncio.Lock()
        self._is_running = False

    def subscribe(self, symbols: List[str]):
        self._subscribed_symbols.update(symbols)

    async def start_background_fetcher(self):
        self._is_running = True
        while self._is_running:
            if self._subscribed_symbols:
                async with self._lock:
                    try:
                        fresh_data = await self.provider.fetch_live_quotes(list(self._subscribed_symbols))
                        self._cache.update(fresh_data)
                        print(f"[DataFeed] Updated {len(fresh_data)} quotes.")
                        
                        # Pass the fresh data to the order monitor to check for SL triggers
                        await order_monitor_service.check_triggers(self._cache)
                        
                    except Exception as e:
                        print(f"[DataFeed] Error fetching: {e}")
            await asyncio.sleep(settings.fetch_interval_seconds)

    async def get_quotes(self, symbols: List[str]) -> Dict[str, LiveQuote]:
        self.subscribe(symbols)
        return {sym: self._cache[sym] for sym in symbols if sym in self._cache}

# Singleton instance
data_feed_service = DataFeedService()
