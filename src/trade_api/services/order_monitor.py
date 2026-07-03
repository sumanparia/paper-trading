import uuid
from collections import defaultdict
from typing import Dict, List
from trade_api.models import LiveQuote, PlaceOrderRequest
from trade_api.database import async_session, TradeRecord
from trade_api.services.quote_service import quote_service
from sqlalchemy import select

class PendingOrder:
    def __init__(self, order_id: str, request: PlaceOrderRequest):
        self.order_id = order_id
        self.instrument_token = request.instrument_token
        self.transaction_type = request.transaction_type
        self.trigger_price = request.trigger_price
        self.quantity = request.quantity
        self.status = "PENDING"

class OrderMonitorService:
    def __init__(self):
        # OPTIMIZATION: Instead of a flat list, group orders by symbol
        # Format: {"RELIANCE.NS": [PendingOrder1, PendingOrder2], "TCS.NS": [PendingOrder3]}
        self.pending_orders: Dict[str, List[PendingOrder]] = defaultdict(list)

    def add_order(self, request: PlaceOrderRequest) -> str:
        """Adds an order to the specific symbol's bucket"""
        order_id = f"ORD_{uuid.uuid4().hex[:10].upper()}"
        order = PendingOrder(order_id, request)
        
        # Add to the specific symbol's list
        self.pending_orders[request.instrument_token].append(order)
        
        print(f"[OrderMonitor] Added SL order {order_id} for {request.instrument_token} at trigger {request.trigger_price}")
        return order_id

    def check_triggers(self, live_quotes: Dict[str, LiveQuote]):
        """
        Called every 2 seconds. Only iterates through symbols that had a price update.
        """
        triggered_ids = []
        
        # We only loop through the symbols that just received new data
        for symbol, current_quote in live_quotes.items():
            
            # Skip if there are no pending orders for this specific symbol
            if symbol not in self.pending_orders:
                continue
                
            orders_to_keep = []
            
            # Check only the orders for THIS symbol
            for order in self.pending_orders[symbol]:
                if order.status != "PENDING":
                    continue

                triggered = False

                # BUY SL triggers when price goes UP to the trigger price
                if order.transaction_type == "BUY" and current_quote.ltp >= order.trigger_price:
                    triggered = True
                    
                # SELL SL triggers when price goes DOWN to the trigger price
                elif order.transaction_type == "SELL" and current_quote.ltp <= order.trigger_price:
                    triggered = True

                if triggered:
                    order.status = "TRIGGERED"
                    triggered_orders.append(order)
                    print(f"🚨 [OrderMonitor] TRIGGERED! {order.order_id} for {symbol}. Cache LTP: {current_quote.ltp}")
                    
                    # Fetch exact execution price from On-Demand pool
                    exact_quote = await quote_service.get_live_quote_now(symbol)
                    final_fill_price = exact_quote.ltp if exact_quote else current_quote.ltp # Fallback to cache if pool totally dies
                    
                    # Save to DB
                    async with async_session() as db:
                        stmt = select(TradeRecord).where(TradeRecord.order_id == order.order_id)
                        result = await db.execute(stmt)
                        db_trade = result.scalar_one_or_none()
                        if db_trade:
                            db_trade.status = "FILLED"
                            db_trade.fill_price = final_fill_price
                            await db.commit()
                            print(f"✅ [DB] Order {order.order_id} filled in DB at {final_fill_price}")
                else:
                    # If not triggered, keep it in the list for the next 2-second check
                    orders_to_keep.append(order)
            
            # Update the list for this symbol (removing triggered ones)
            self.pending_orders[symbol] = orders_to_keep

        # Optional: In a real system, you would pass `triggered_ids` to an Execution Engine here

# Singleton
order_monitor_service = OrderMonitorService()