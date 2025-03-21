from datetime import datetime
from collections import namedtuple
import random
from .base import BaseExchange

OrderResponse = namedtuple('OrderResponse', ['order_id', 'symbol', 'side', 'quantity', 'price', 'status', 'timestamp'])

class PaperTradingExchange(BaseExchange):
    def __init__(self, config=None):
        if config is None:
            config = {
                'risk_management': {
                    'position_size': {'max_trade_size': 1.0},
                    'stop_loss': {'type': 'trailing', 'activation_percent': 1.0, 'trail_percent': 0.5}
                }
            }
        super().__init__(config)
        self.balance = 10000.0  # Initial balance in USDT
        self.positions = {}  # symbol -> {quantity, entry_price}
        self.order_counter = 0
        self.last_price = 50000.0  # Initial BTC price
        self.orders = {}  # order_id -> OrderResponse

    async def connect(self):
        """Connect to the exchange."""
        return True

    async def get_balance(self) -> dict:
        """Get balance for all assets."""
        btc_balance = sum(pos['quantity'] for pos in self.positions.values())
        btc_value = btc_balance * self.last_price
        return {
            'USDT': round(self.balance, 2),
            'BTC': round(btc_balance, 8),
            'total': round(self.balance + btc_value, 2)
        }

    async def get_balances(self):
        """Get all account balances."""
        return await self.get_balance()

    async def get_positions(self):
        """Get open positions."""
        positions = []
        for symbol, pos in self.positions.items():
            current_price = await self.get_market_price(symbol)
            pnl = (current_price - pos['entry_price']) * pos['quantity']
            positions.append({
                'symbol': symbol,
                'quantity': round(pos['quantity'], 8),
                'entry_price': round(pos['entry_price'], 2),
                'current_price': round(current_price, 2),
                'pnl': round(pnl, 2)
            })
        return positions

    async def get_market_price(self, symbol: str) -> float:
        """Get current market price."""
        self.last_price = self._get_simulated_price()
        return self.last_price

    async def place_order(self, symbol: str, side: str, quantity: float, price: float = None) -> OrderResponse:
        """Place a paper trade order."""
        self.order_counter += 1
        order_id = f'paper_order_{self.order_counter}'
        
        # Get current price
        price = await self.get_market_price(symbol)
        
        # Update positions and balance
        if side == 'buy':
            cost = price * quantity
            if cost > self.balance:
                raise ValueError("Insufficient balance")
            
            self.balance -= cost
            if symbol not in self.positions:
                self.positions[symbol] = {
                    'symbol': symbol,
                    'quantity': quantity,
                    'entry_price': price
                }
            else:
                # Update position with weighted average entry price
                current_pos = self.positions[symbol]
                total_quantity = current_pos['quantity'] + quantity
                current_pos['entry_price'] = (
                    (current_pos['quantity'] * current_pos['entry_price'] + quantity * price) 
                    / total_quantity
                )
                current_pos['quantity'] = total_quantity
            
        else:  # sell
            if symbol not in self.positions or self.positions[symbol]['quantity'] < quantity:
                raise ValueError("Insufficient position size")
            
            revenue = price * quantity
            self.balance += revenue
            
            # Update position
            current_pos = self.positions[symbol]
            current_pos['quantity'] -= quantity
            if current_pos['quantity'] <= 0:
                del self.positions[symbol]

        order = OrderResponse(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            status='filled',
            timestamp=datetime.now()
        )
        
        self.orders[order_id] = order
        return order

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        if order_id in self.orders:
            del self.orders[order_id]
            return True
        return False

    async def update_position(self, symbol: str, quantity: float, price: float):
        """Update position after trade."""
        if symbol not in self.positions:
            if quantity > 0:
                self.positions[symbol] = {
                    'symbol': symbol,
                    'quantity': quantity,
                    'entry_price': price
                }
        else:
            current_pos = self.positions[symbol]
            new_quantity = current_pos['quantity'] + quantity
            
            if new_quantity <= 0:
                del self.positions[symbol]
            else:
                # Update position with weighted average entry price
                if quantity > 0:
                    current_pos['entry_price'] = (
                        (current_pos['quantity'] * current_pos['entry_price'] + quantity * price) 
                        / new_quantity
                    )
                current_pos['quantity'] = new_quantity

    async def close_position(self, symbol: str) -> OrderResponse:
        """Close an entire position."""
        if symbol not in self.positions:
            raise ValueError(f"No position found for {symbol}")
            
        position = self.positions[symbol]
        return await self.place_order(
            symbol=symbol,
            side='sell',
            quantity=position['quantity']
        )

    def _get_simulated_price(self) -> float:
        """Simulate price movement."""
        change_percent = random.uniform(-0.1, 0.1)  # -0.1% to +0.1% change
        self.last_price *= (1 + change_percent)
        return self.last_price
