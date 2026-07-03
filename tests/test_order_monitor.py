import pytest
from unittest.mock import AsyncMock, patch
from trade_api.services.order_monitor import OrderMonitorService
from trade_api.models import PlaceOrderRequest, TransactionType, OrderType, LiveQuote

@pytest.mark.asyncio
async def test_sl_order_does_not_trigger_prematurely():
    monitor = OrderMonitorService()

    req = PlaceOrderRequest(
        instrument_token="RELIANCE.NS",
        transaction_type=TransactionType.SELL,
        order_type=OrderType.SL,
        quantity=1,
        trigger_price=90.0
    )
    monitor.add_order(req)

    # Simulate a 2-second tick where price is 95.0 (Above trigger)
    fake_quotes = {"RELIANCE.NS": LiveQuote(
        instrument_id="RELIANCE.NS", symbol="RELIANCE.NS", ltp=95.0,
        open=95, high=96, low=94, close=95, volume=100
    )}
    await monitor.check_triggers(fake_quotes)

    # Assert it is still pending
    assert len(monitor.pending_orders["RELIANCE.NS"]) == 1
    assert monitor.pending_orders["RELIANCE.NS"][0].status == "PENDING"

@pytest.mark.asyncio
async def test_sl_order_triggers_correctly():
    monitor = OrderMonitorService()

    req = PlaceOrderRequest(
        instrument_token="RELIANCE.NS",
        transaction_type=TransactionType.SELL,
        order_type=OrderType.SL,
        quantity=1,
        trigger_price=90.0
    )
    monitor.add_order(req)

    # Simulate a tick where price drops to 89.5 (Below trigger)
    fake_quotes = {"RELIANCE.NS": LiveQuote(
        instrument_id="RELIANCE.NS", symbol="RELIANCE.NS", ltp=89.5,
        open=90, high=90, low=89, close=89.5, volume=100
    )}

    # Mock the quote_service and DB session used inside check_triggers
    with patch("trade_api.services.order_monitor.quote_service") as mock_qs, \
         patch("trade_api.services.order_monitor.async_session") as mock_session:
        mock_qs.get_live_quote_now = AsyncMock(return_value=LiveQuote(
            instrument_id="RELIANCE.NS", symbol="RELIANCE.NS", ltp=89.5,
            open=90, high=90, low=89, close=89.5, volume=100
        ))
        # Mock the async context manager for DB session
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=lambda: None))
        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session.return_value.__aexit__ = AsyncMock(return_value=False)

        await monitor.check_triggers(fake_quotes)

    # Assert it was removed from pending orders (triggered)
    assert len(monitor.pending_orders["RELIANCE.NS"]) == 0