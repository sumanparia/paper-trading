from fastapi import APIRouter, HTTPException
from trade_api.models import PlaceSmartOrderRequest, OrderResponse
import uuid

router = APIRouter(prefix="/smart-orders", tags=["Smart Orders"])

@router.post(
    "/place", 
    response_model=OrderResponse,
    summary="Place Smart Order",
    description="Places a smart/bracket order with mandatory exit triggers. Parameters strictly match Groww SDK."
)
async def place_smart_order(request: PlaceSmartOrderRequest):
    if not request.exit_trigger_price:
        raise HTTPException(status_code=400, detail="exit_trigger_price is mandatory for smart orders")

    mock_order_id = f"SMART_{uuid.uuid4().hex[:10].upper()}"
    
    # In a real app, this would place the main order and attach the exit legs
    return OrderResponse(
        order_id=mock_order_id,
        status="ACCEPTED",
        message=f"Mock Smart Order placed for {request.instrument_token}. SL: {request.exit_trigger_price}, Target: {request.exit_price}"
    )