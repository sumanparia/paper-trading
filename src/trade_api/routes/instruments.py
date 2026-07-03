from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from trade_api.models import Instrument

router = APIRouter(prefix="/instruments", tags=["Instruments"])

# Mock database of instruments
MOCK_INSTRUMENTS_DB = [
    Instrument(
        instrument_token="NSE:RELIANCE", trading_symbol="RELIANCE", name="Reliance Industries Ltd",
        exchange="NSE", instrument_type="EQ", lot_size=250, isin="INE002A01018"
    ),
    Instrument(
        instrument_token="NSE:TCS", trading_symbol="TCS", name="Tata Consultancy Services Ltd",
        exchange="NSE", instrument_type="EQ", lot_size=150, isin="INE467B01029"
    ),
    Instrument(
        instrument_token="NFO:RELIANCE24DEC2500CE", trading_symbol="RELIANCE24DEC2500CE", name="Reliance Industries Ltd",
        exchange="NFO", instrument_type="OPT", lot_size=250, expiry="2024-12-26", strike_price=2500.0
    ),
    Instrument(
        instrument_token="NFO:NIFTY24DECFUT", trading_symbol="NIFTY24DECFUT", name="NIFTY",
        exchange="NFO", instrument_type="FUT", lot_size=25, expiry="2024-12-26"
    )
]

@router.get(
    "", 
    response_model=List[Instrument],
    summary="Get Instruments Master List",
    description="Fetches the list of all instruments. Matches Groww SDK instruments.get_instruments(). "
                "Supports optional filtering by exchange, instrument_type, or trading_symbol."
)
async def get_instruments(
    exchange: Optional[str] = Query(None, description="Filter by exchange (e.g., NSE, NFO)"),
    instrument_type: Optional[str] = Query(None, description="Filter by type (e.g., EQ, FUT, OPT)"),
    symbol: Optional[str] = Query(None, description="Search by trading symbol (partial match)")
):
    results = MOCK_INSTRUMENTS_DB
    
    if exchange:
        results = [inst for inst in results if inst.exchange.upper() == exchange.upper()]
    if instrument_type:
        results = [inst for inst in results if inst.instrument_type.upper() == instrument_type.upper()]
    if symbol:
        results = [inst for inst in results if symbol.upper() in inst.trading_symbol.upper()]
        
    return results

@router.get(
    "/{instrument_token}", 
    response_model=Instrument,
    summary="Get Instrument Details",
    description="Fetches details of a specific instrument using its token. Matches Groww SDK instruments.get_instrument_by_token()."
)
async def get_instrument_by_token(instrument_token: str):
    for inst in MOCK_INSTRUMENTS_DB:
        if inst.instrument_token == instrument_token:
            return inst
            
    raise HTTPException(status_code=404, detail=f"Instrument '{instrument_token}' not found.")