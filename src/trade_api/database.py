from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from datetime import datetime

# SQLite database file will be created in the project root
DATABASE_URL = "sqlite+aiosqlite:///./trading_db.sqlite"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class TradeRecord(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    instrument_token = Column(String, index=True)
    transaction_type = Column(String) # BUY or SELL
    order_type = Column(String)      # MARKET, LIMIT, SL
    quantity = Column(Integer)
    fill_price = Column(Float, nullable=True) # Null for SL until triggered
    status = Column(String)          # FILLED, PENDING, TRIGGERED
    created_at = Column(DateTime, default=func.now())

# Create tables on startup
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dependency to get DB session in routes
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session