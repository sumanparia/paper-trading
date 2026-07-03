import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from trade_api.main import app
from trade_api.models import LiveQuote

@pytest.mark.asyncio
async def test_place_market_order_saves_to_db(override_get_db):
    """Test that placing a market order hits the provider, gets price, and saves to DB"""
    
    # 1. Mock the Database dependency
    app.dependency_overrides[override_get_db.__wrapped__] = override_get_db
    
    # 2. Mock the QuoteService to return a fake price instantly
    with patch("trade_api.routes.orders.quote_service") as mock_service:
        mock_service.get_live_quote_now.return_value = LiveQuote(
            instrument_id="RELIANCE.NS", symbol="RELIANCE.NS", ltp=2500.0, 
            open=2490, high=2510, low=2480, close=2495, volume=1000
        )
        
        # 3. Hit the API
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/orders/place", json={
                "instrument_token": "RELIANCE.NS",
                "transaction_type": "BUY",
                "order_type": "MARKET",
                "quantity": 10
            })
        
        # 4. Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FILLED"
        assert data["average_price"] == 2500.0
        assert data["order_id"].startswith("ORD_")
        
        # Verify the mock was called exactly once
        mock_service.get_live_quote_now.assert_called_once_with("RELIANCE.NS")
        
    # Clean up override
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_place_sl_order_does_not_hit_provider(override_get_db):
    """Test that an SL order is PENDING and does NOT ask the provider for a price"""
    
    app.dependency_overrides[override_get_db.__wrapped__] = override_get_db
    
    with patch("trade_api.routes.orders.quote_service") as mock_service:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/orders/place", json={
                "instrument_token": "TCS.NS",
                "transaction_type": "SELL",
                "order_type": "SL",
                "quantity": 5,
                "trigger_price": 3400.0
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING"
        assert data["average_price"] is None
        
        # CRITICAL ASSERTION: Ensure we DID NOT hammer the API for an SL order
        mock_service.get_live_quote_now.assert_not_called()
        
    app.dependency_overrides.clear()