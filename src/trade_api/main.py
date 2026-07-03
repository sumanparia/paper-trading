import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import markdown

from trade_api.config import settings
from trade_api.providers import get_provider
from trade_api.services.data_feed import data_feed_service
# Add smart_orders to the import line below:
from trade_api.routes import live_data, orders, portfolio, instruments, smart_orders
from trade_api.routes import live_data, orders, portfolio, instruments, smart_orders, margin, analytics
from trade_api.database import init_db
from trade_api.routes import live_data, orders, portfolio, instruments, smart_orders, margin, analytics, historical


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database
    await init_db()
    print("[DB] Database initialized and tables created.")
    
    # 1. Build the Provider Pool from config
    provider_pool = get_provider_pool()
    
    # 2. Give the whole pool to the On-Demand Execution Service
    init_quote_service(provider_pool)
    
    # 3. Give ONLY the first provider to the Background Cache 
    # (This prevents hammering ALL providers every 2 seconds in the background)
    data_feed_service.provider = provider_pool[0] if provider_pool else None
    fetcher_task = asyncio.create_task(data_feed_service.start_background_fetcher())

    yield
    data_feed_service._is_running = False
    fetcher_task.cancel()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(live_data.router)
app.include_router(orders.router)
app.include_router(smart_orders.router) # Register the new router
app.include_router(portfolio.router)
app.include_router(instruments.router)
app.include_router(live_data.router)
app.include_router(orders.router)
app.include_router(smart_orders.router)
app.include_router(portfolio.router)
app.include_router(instruments.router)
app.include_router(margin.router)
app.include_router(analytics.router)
app.include_router(historical.router)  # Register the historical data router

@app.get("/docs/guide", response_class=HTMLResponse, tags=["Documentation"])
async def read_markdown_docs():
    try:
        with open("docs/API_REFERENCE.md", "r", encoding="utf-8") as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code"])
        return f"""
        <html>
            <head><title>Trade API Guide</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; line-height: 1.6; color: #333; }}
                pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
            </style>
            </head>
            <body>{html_content}</body>
        </html>
        """
    except FileNotFoundError:
        return HTMLResponse("<h1>Documentation not found</h1><p>Ensure docs/API_REFERENCE.md exists.</p>", status_code=404)

@app.get("/")
async def root():
    return {
        "message": "Trade API Server is running", 
        "provider": settings.data_provider,
        "interactive_swagger": "http://localhost:8000/docs",
        "written_guide": "http://localhost:8000/docs/guide"
    }