from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OrderRequest:
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    order_type: str  # 'market' or 'limit'
    price: Optional[float] = None  # Required for limit orders
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class OrderResponse:
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    timestamp: datetime

@dataclass
class Position:
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    timestamp: datetime

class BaseExchange(ABC):
    """Base class for all exchange implementations."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.positions: Dict[str, Position] = {}
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the exchange."""
        pass
    
    @abstractmethod
    async def get_market_price(self, symbol: str) -> float:
        """Get current market price for a symbol."""
        pass
    
    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance."""
        pass
    
    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place a new order."""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get current positions."""
        pass
    
    @abstractmethod
    async def update_position(self, symbol: str, current_price: float) -> None:
        """Update position with current market price."""
        pass
    
    @abstractmethod
    async def close_position(self, symbol: str) -> OrderResponse:
        """Close an existing position."""
        pass
    
    async def validate_order(self, order: OrderRequest) -> bool:
        """Validate order parameters."""
        if order.order_type == 'limit' and order.price is None:
            raise ValueError("Limit orders require a price")
        
        if order.quantity <= 0:
            raise ValueError("Order quantity must be positive")
        
        # Check against max trade size from config
        max_trade_size = self.config['risk_management']['position_size']['max_trade_size']
        if order.quantity > max_trade_size:
            raise ValueError(f"Order quantity exceeds maximum trade size of {max_trade_size}")
        
        return True
    
    def calculate_pnl(self, position: Position, current_price: float) -> float:
        """Calculate unrealized PnL for a position."""
        if position.side == 'buy':
            return (current_price - position.entry_price) * position.quantity
        else:
            return (position.entry_price - current_price) * position.quantity

    async def check_trailing_stop(self, symbol: str, current_price: float) -> bool:
        """Check if trailing stop loss has been triggered."""
        position = self.positions.get(symbol)
        if not position:
            return False
            
        stop_loss_config = self.config['risk_management']['stop_loss']
        if stop_loss_config['type'] != 'trailing':
            return False
            
        # Calculate profit percentage
        profit_percent = ((current_price - position.entry_price) / position.entry_price) * 100
        
        # Check if trailing stop loss should be activated
        if profit_percent >= stop_loss_config['activation_percent']:
            trail_percent = stop_loss_config['trail_percent']
            highest_price = max(position.entry_price * (1 + profit_percent/100), current_price)
            
            # Check if price has fallen below trailing stop
            if current_price <= highest_price * (1 - trail_percent/100):
                return True
                
        return False
