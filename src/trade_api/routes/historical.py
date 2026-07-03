from fastapi import APIRouter, HTTPException, Query
from typing import List
from trade_api.models import HistoricalCandle
from trade_api.services.quote_service import quote_service # We can use the pool for this too!

router = APIRouter(prefix="/historical-data", tags=["Historical Data"])

@router.get(
    "", 
    response_model=List[HistoricalCandle],
    summary="Get Historical Data",
    description="Fetches historical OHLCV candle data. Matches Groww SDK historical_data.get_historical_data(). "
                "Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 1d, 1w, 1mo. "
                "start_time and end_time are UNIX epoch timestamps in seconds."
)
async def get_historical_data(
    instrument_token: str = Query(..., description="e.g., RELIANCE.NS"),
    interval: str = Query("1d", description="Candle interval (e.g., 5m, 1h, 1d)"),
    start_time: int = Query(..., description="Start epoch timestamp in seconds"),
    end_time: int = Query(..., description="End epoch timestamp in seconds")
):
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="start_time must be before end_time")

    # We use the provider pool! If Yahoo fails to get history, it falls back to Finnhub
    # (Assuming you implemented fetch_historical_data in Finnhub provider too)
    provider = quote_service.providers[0] if quote_service and quote_service.providers else None
    
    if not provider:
        raise HTTPException(status_code=503, detail="No data providers configured.")

    try:
        candles = await provider.fetch_historical_data(
            symbol=instrument_token,
            interval=interval,
            start=start_time,
            end=end_time
        )
        
        if not candles:
            raise HTTPException(status_code=404, detail="No historical data found for this instrument/period.")
            
        return candles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical data: {str(e)}")