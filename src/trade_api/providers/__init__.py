from typing import List
from trade_api.config import settings
from trade_api.providers.base import DataProvider

def get_provider_pool() -> List[DataProvider]:
    """Returns a list of instantiated providers based on priority config."""
    pool = []
    
    for provider_name in settings.provider_pool:
        if provider_name == "finnhub":
            from trade_api.providers.finnhub import FinnhubProvider
            pool.append(FinnhubProvider())
        elif provider_name == "yahoo":
            from trade_api.providers.yahoo import YahooProvider
            pool.append(YahooProvider())
        # Easy to add more later:
        # elif provider_name == "polygon":
        #     from trade_api.providers.polygon import PolygonProvider
        #     pool.append(PolygonProvider())
            
    if not pool:
        raise ValueError("No valid providers found in PROVIDER_POOL config!")
        
    return pool