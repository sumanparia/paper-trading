import pytest
import asyncio
from typing import List, Dict
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from trade_api.providers.base import DataProvider
from trade_api.models import LiveQuote, HistoricalCandle, PlaceOrderRequest, TransactionType, OrderType
from trade_api.database import Base, get_db
from trade_api.services.quote_service import QuoteService

# --- 1. MOCK PROVIDERS ---

class MockSuccessProvider(DataProvider):
    """A fake provider that always returns good data"""
    async def fetch_live_quotes(self, symbols: List[str]) -> Dict[str, LiveQuote]:
        return {sym: LiveQuote(instrument_id=sym, symbol=sym, ltp=100.0, open=99.0, high=101.0, low=98.0, close=99.5, volume=1000) for sym in symbols}

    async def fetch_historical_data(self, symbol: str, interval: str, start: int, end: int) -> List[HistoricalCandle]:
        return [HistoricalCandle(timestamp=start, open=100, high=101, low=99, close=100.5, volume=500)]

class MockFailingProvider(DataProvider):
    """A fake provider that always throws an exception (Simulates Yahoo/Finnhub downtime)"""
    async def fetch_live_quotes(self, symbols: List[str]) -> Dict[str, LiveQuote]:
        raise ConnectionError("API Rate Limit Exceeded")

    async def fetch_historical_data(self, symbol: str, interval: str, start: int, end: int) -> List[HistoricalCandle]:
        raise ConnectionError("API Rate Limit Exceeded")

# --- 2. MOCK DATABASE ---

SQLALCHEMY_TEST_URL = "sqlite+aiosqlite:///./test_db.sqlite"
test_engine = create_async_engine(SQLALCHEMY_TEST_URL, echo=False)
TestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function")
async def db_session():
    # Create tables for this specific test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    # Drop tables after test to keep it clean
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Override the dependency in FastAPI
@pytest.fixture(scope="function")
def override_get_db(db_session):
    async def _override():
        yield db_session
    return _override