from typing import Optional, List
from trade_api.models import LiveQuote
from trade_api.providers.base import DataProvider

class QuoteService:
    def __init__(self, providers: List[DataProvider]):
        self.providers = providers

    async def get_live_quote_now(self, symbol: str) -> Optional[LiveQuote]:
        """
        Iterates through the provider pool sequentially.
        Tries Provider A, if it fails/returns bad data, tries Provider B, etc.
        """
        for index, provider in enumerate(self.providers):
            provider_name = type(provider).__name__
            try:
                quotes = await provider.fetch_live_quotes([symbol])
                
                # Validate the data actually exists and isn't zero
                if symbol in quotes and quotes[symbol].ltp > 0:
                    if index > 0:
                        print(f"[QuoteService] Provider {index} ({provider_name}) succeeded for {symbol}.")
                    return quotes[symbol]
                else:
                    print(f"[QuoteService] Provider {index} ({provider_name}) returned empty/zero data for {symbol}. Trying next...")
                    
            except Exception as e:
                print(f"[QuoteService] Provider {index} ({provider_name}) FAILED for {symbol}: {str(e)[:50]}. Trying next...")

        # If we get here, the entire pool failed
        print(f"[QuoteService] CRITICAL: Entire provider pool exhausted for {symbol}.")
        return None

# Singleton instance
quote_service: Optional[QuoteService] = None

def init_quote_service(providers: List[DataProvider]):
    global quote_service
    quote_service = QuoteService(providers)
    print(f"[QuoteService] Initialized with {len(providers)} providers in pool.")