import pytest
from trade_api.services.quote_service import QuoteService
from conftest import MockSuccessProvider, MockFailingProvider

@pytest.mark.asyncio
async def test_provider_pool_fallback_mechanism():
    """Test that if the primary provider fails, the pool falls back to the secondary."""
    # Pool: [Failing Provider, Success Provider]
    pool = QuoteService(providers=[MockFailingProvider(), MockSuccessProvider()])
    
    # Act
    quote = await pool.get_live_quote_now("RELIANCE.NS")
    
    # Assert
    assert quote is not None, "Pool should have returned data from fallback"
    assert quote.ltp == 100.0
    assert quote.symbol == "RELIANCE.NS"

@pytest.mark.asyncio
async def test_provider_pool_total_failure():
    """Test that if ALL providers fail, it returns None gracefully."""
    pool = QuoteService(providers=[MockFailingProvider(), MockFailingProvider()])
    
    quote = await pool.get_live_quote_now("TCS.NS")
    
    assert quote is None, "Pool should return None when all providers fail"