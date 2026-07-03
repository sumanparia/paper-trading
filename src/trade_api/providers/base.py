from abc import ABC, abstractmethod
from typing import List, Dict
from trade_api.models import LiveQuote, HistoricalCandle

class DataProvider(ABC):
    @abstractmethod
    async def fetch_live_quotes(self, symbols: List[str]) -> Dict[str, LiveQuote]:
        pass

    @abstractmethod
    async def fetch_historical_data(self, symbol: str, interval: str, start: int, end: int) -> List[HistoricalCandle]:
        pass
