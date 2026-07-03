from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

# --- Enums for strict validation (Matches Groww Docs) ---
class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"

class ProductType(str, Enum):
    CNC = "CNC"       # Delivery
    MIS = "MIS"       # Intraday
    BO = "BO"         # Bracket Order
    CO = "CO"         # Cover Order

class Validity(str, Enum):
    DAY = "DAY"
    IOC = "IOC"       # Immediate or Cancel

# --- Core Data Models ---
class Instrument(BaseModel):
    instrument_token: str = Field(..., description="Unique identifier (e.g., NSE:RELIANCE)")
    trading_symbol: str = Field(..., description="Trading symbol (e.g., RELIANCE)")
    name: str = Field(..., description="Full legal name of the company/instrument")
    exchange: str = Field(..., description="NSE, BSE, NFO, MCX, etc.")
    instrument_type: str = Field(..., description="EQ, FUT, OPT, etc.")
    lot_size: Optional[int] = Field(None, description="Lot size (mainly for F&O)")
    tick_size: Optional[float] = Field(0.05, description="Minimum price movement")
    isin: Optional[str] = Field(None, description="ISIN code for equities")
    expiry: Optional[str] = Field(None, description="Expiry date (YYYY-MM-DD) for F&O")
    strike_price: Optional[float] = Field(None, description="Strike price for Options")

class LiveQuote(BaseModel):
    instrument_id: str
    symbol: str
    ltp: float
    open: float
    high: float
    low: float
    close: float
    volume: int

class HistoricalCandle(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int

# --- Order Models (Exact Groww Parameters) ---
class PlaceOrderRequest(BaseModel):
    instrument_token: str = Field(..., description="Exchange:Symbol (e.g., NSE:RELIANCE) or Token ID")
    transaction_type: TransactionType
    order_type: OrderType
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(None, description="Required for LIMIT and SL orders")
    trigger_price: Optional[float] = Field(None, description="Required for SL and SL-M orders")
    validity: Validity = Validity.DAY
    product: ProductType = ProductType.CNC
    disclosed_quantity: Optional[int] = Field(0, description="Quantity to disclose in market depth")
    tag: Optional[str] = Field(None, description="Optional strategy tag")

class PlaceSmartOrderRequest(BaseModel):
    instrument_token: str = Field(..., description="Exchange:Symbol (e.g., NSE:RELIANCE)")
    transaction_type: TransactionType
    order_type: OrderType = OrderType.MARKET # Smart orders are usually market with SL/Target
    quantity: int = Field(..., gt=0)
    price: Optional[float] = None
    product: ProductType = ProductType.BO # Smart orders default to Bracket Orders
    validity: Validity = Validity.DAY
    # Smart Order Specific Fields
    exit_trigger_price: float = Field(..., description="Stop loss price for the smart order")
    exit_price: Optional[float] = Field(None, description="Target price for the smart order")
    trailing_sl: Optional[bool] = Field(False, description="Enable trailing stop loss")

class OrderResponse(BaseModel):
    order_id: str
    status: str = "ACCEPTED"
    message: Optional[str] = None
    average_price: Optional[float] = None

# Portfolio Models
class Holding(BaseModel):
    instrument_token: str
    symbol: str
    exchange: str
    quantity: int
    average_price: float
    close_price: float
    pnl: float
    pnl_percentage: float

class Position(BaseModel):
    instrument_token: str
    symbol: str
    exchange: str
    product: str
    quantity: int
    buy_avg: float
    sell_avg: float
    pnl: float

# Margin Models
class MarginSegment(BaseModel):
    used: float = Field(..., description="Margin currently utilized")
    available: float = Field(..., description="Margin currently free to use")
    total: float = Field(..., description="Total margin (cash + collateral)")

class MarginResponse(BaseModel):
    equity: MarginSegment
    commodity: MarginSegment
    fno: MarginSegment  # Futures & Options
    currency: MarginSegment