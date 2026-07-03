from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str = "Groww-Like Trade API"
    
    # Define the priority order of your data providers
    provider_pool: List[str] = ["yahoo", "finnhub"] 
    
    # Background feed will only use the FIRST provider in the list to save API limits
    fetch_interval_seconds: int = 2
    finnhub_api_key: str = "YOUR_FINNHUB_API_KEY"

    class Config:
        env_file = ".env"

settings = Settings()