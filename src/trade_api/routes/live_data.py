from fastapi import APIRouter, HTTPException
from typing import List
from trade_api.models import LiveQuote
from trade_api.services.data_feed import data_feed_service

router = APIRouter(tags=["Live Market Data"])

@router.get(
    "/live-data/quote", 
    response_model=List[LiveQuote],
    summary="Get Live Quotes",
    description="Fetches the latest cached market quotes for given symbols. "
                "Note: Data is updated in the background every 2 seconds. Passing a new symbol subscribes it to the background fetcher."
)
async def get_live_quotes(
    symbols: str = "RELIANCE.NS,TCS.NS",
    description="Comma-separated list of symbols (Yahoo Finance format, e.g., RELIANCE.NS)"
):
    symbol_list = [s.strip() for s in symbols.split(",")]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="No symbols provided")
    
    quotes_dict = await data_feed_service.get_quotes(symbol_list)
    
    if not quotes_dict:
        raise HTTPException(status_code=404, detail="Data not yet available. Please retry in a few seconds.")
        
    return list(quotes_dict.values())