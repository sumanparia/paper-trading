from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from trade_api.database import get_db, TradeRecord
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["Analytics"])

class SymbolPnL(BaseModel):
    symbol: str
    total_buy_qty: int
    total_sell_qty: int
    average_buy_price: float
    average_sell_price: float
    net_position: int
    realized_pnl: float

@router.get("/eod-pnl", response_model=list[SymbolPnL])
async def get_eod_pnl(db: AsyncSession = Depends(get_db)):
    """
    Calculates End of Day Profit & Loss based on all FILLED trades in the database.
    """
    # Fetch all executed trades
    stmt = select(TradeRecord).where(TradeRecord.status == "FILLED")
    result = await db.execute(stmt)
    trades = result.scalars().all()

    # Group by symbol
    symbol_data = {}
    for trade in trades:
        if trade.instrument_token not in symbol_data:
            symbol_data[trade.instrument_token] = {"buy_qty": 0, "buy_value": 0.0, "sell_qty": 0, "sell_value": 0.0}
        
        if trade.transaction_type == "BUY":
            symbol_data[trade.instrument_token]["buy_qty"] += trade.quantity
            symbol_data[trade.instrument_token]["buy_value"] += (trade.fill_price * trade.quantity)
        elif trade.transaction_type == "SELL":
            symbol_data[trade.instrument_token]["sell_qty"] += trade.quantity
            symbol_data[trade.instrument_token]["sell_value"] += (trade.fill_price * trade.quantity)

    pnl_report = []
    for symbol, data in symbol_data.items():
        avg_buy = data["buy_value"] / data["buy_qty"] if data["buy_qty"] > 0 else 0
        avg_sell = data["sell_value"] / data["sell_qty"] if data["sell_qty"] > 0 else 0
        
        # Realized PnL is simply Money Received - Money Spent
        realized_pnl = data["sell_value"] - data["buy_value"]
        net_position = data["buy_qty"] - data["sell_qty"]

        pnl_report.append(SymbolPnL(
            symbol=symbol,
            total_buy_qty=data["buy_qty"],
            total_sell_qty=data["sell_qty"],
            average_buy_price=round(avg_buy, 2),
            average_sell_price=round(avg_sell, 2),
            net_position=net_position,
            realized_pnl=round(realized_pnl, 2)
        ))

    return pnl_report