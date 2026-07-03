from fastapi import APIRouter
from trade_api.models import Holding, Position
from typing import List

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get(
    "/holdings", 
    response_model=List[Holding],
    summary="Get Holdings",
    description="Returns a list of all equity holdings (CNC/Delivery) in the account. Matches Groww SDK portfolio.get_holdings() output."
)
async def get_holdings():
    # Mock data exactly matching Groww's schema
    return [
        Holding(
            instrument_token="NSE:RELIANCE",
            symbol="RELIANCE",
            exchange="NSE",
            quantity=10,
            average_price=2450.50,
            close_price=2505.25,
            pnl=547.50,
            pnl_percentage=2.23
        ),
        Holding(
            instrument_token="NSE:TCS",
            symbol="TCS",
            exchange="NSE",
            quantity=5,
            average_price=3800.00,
            close_price=3750.00,
            pnl=-250.00,
            pnl_percentage=-1.31
        )
    ]

@router.get(
    "/positions", 
    response_model=List[Position],
    summary="Get Open Positions",
    description="Returns a list of all open intraday (MIS) or derivative positions. Matches Groww SDK portfolio.get_positions() output."
)
async def get_positions():
    # Mock data exactly matching Groww's schema
    return [
        Position(
            instrument_token="NSE:INFY",
            symbol="INFY",
            exchange="NSE",
            product="MIS",
            quantity=-50, # Negative for short
            buy_avg=0.0,
            sell_avg=1520.50,
            pnl=1250.00
        )
    ]