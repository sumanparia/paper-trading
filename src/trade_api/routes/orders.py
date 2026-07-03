from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from trade_api.models import PlaceOrderRequest, OrderResponse
from trade_api.database import get_db, TradeRecord
from trade_api.services.order_monitor import order_monitor_service
from trade_api.services.quote_service import quote_service
import uuid

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/place", response_model=OrderResponse)
async def place_order(
    request: PlaceOrderRequest,
    db: AsyncSession = Depends(get_db)
):
    if request.order_type == "LIMIT" and request.price is None:
        raise HTTPException(status_code=400, detail="Price is required for LIMIT orders")
    if request.order_type in ["SL", "SL-M"] and request.trigger_price is None:
        raise HTTPException(status_code=400, detail="Trigger price is required for SL/SL-M orders")

    order_id = f"ORD_{uuid.uuid4().hex[:10].upper()}"
    fill_price = None
    status = "PENDING"

    # --- MARKET ORDER: Direct Provider Fetch ---
    if request.order_type == "MARKET":
        try:
            live_quote = await quote_service.get_live_quote_now(request.instrument_token)

            if not live_quote or live_quote.ltp <= 0:
                raise HTTPException(status_code=503, detail="All data providers failed to fetch price. Order rejected.")

            fill_price = live_quote.ltp
            status = "FILLED"
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to fetch price: {str(e)}")

    # --- LIMIT ORDER ---
    elif request.order_type == "LIMIT":
        fill_price = request.price
        status = "PLACED"

    # --- SL / SL-M: Go to background monitor ---
    elif request.order_type in ["SL", "SL-M"]:
        order_monitor_service.add_order(request)
        status = "PENDING"
        fill_price = None

    # --- SAVE TO DATABASE ---
    db_trade = TradeRecord(
        order_id=order_id,
        instrument_token=request.instrument_token,
        transaction_type=request.transaction_type.value,
        order_type=request.order_type.value,
        quantity=request.quantity,
        fill_price=fill_price,
        status=status
    )
    db.add(db_trade)
    await db.commit()

    return OrderResponse(
        order_id=order_id,
        status=status,
        message=f"Order processed via provider pool and saved to DB.",
        average_price=fill_price
    )