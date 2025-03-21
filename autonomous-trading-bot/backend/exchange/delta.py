import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import hmac
import hashlib
import time
import aiohttp
from .base import BaseExchange, OrderRequest, OrderResponse, Position
from ..logger import logger

class DeltaExchange(BaseExchange):
    """Delta Exchange implementation."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config['exchange']['apiKey']
        self.api_secret = config['exchange']['secret']
        self.base_url = config['exchange']['base_url']
        self.session = None
        
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = '') -> str:
        """Generate signature for Delta Exchange API authentication."""
        message = timestamp + method + path + body
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
        
    async def _request(self, method: str, path: str, data: Dict = None) -> Dict:
        """Make authenticated request to Delta Exchange API."""
        if self.session is None:
            raise ValueError("Exchange not connected. Call connect() first.")
            
        timestamp = str(int(time.time() * 1000))
        body = '' if data is None else str(data)
        signature = self._generate_signature(timestamp, method, path, body)
        
        headers = {
            'api-key': self.api_key,
            'timestamp': timestamp,
            'signature': signature,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{path}"
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Delta Exchange API error: {error_text}")
                    raise ValueError(f"API request failed: {error_text}")
                    
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Network error in Delta Exchange API request: {str(e)}")
            raise
            
    async def connect(self) -> bool:
        """Establish connection to Delta Exchange."""
        self.session = aiohttp.ClientSession()
        
        try:
            # Test connection with a simple API call
            await self._request('GET', '/v2/time')
            logger.info("Successfully connected to Delta Exchange")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Delta Exchange: {str(e)}")
            return False
            
    async def get_market_price(self, symbol: str) -> float:
        """Get current market price from Delta Exchange."""
        response = await self._request('GET', f'/v2/tickers/{symbol}')
        return float(response['mark_price'])
        
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance from Delta Exchange."""
        response = await self._request('GET', '/v2/wallet/balances')
        balances = {}
        for balance in response:
            balances[balance['currency']] = float(balance['available_balance'])
        return balances
        
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order on Delta Exchange."""
        await self.validate_order(order)
        
        data = {
            'symbol': order.symbol,
            'side': order.side.upper(),
            'size': order.quantity,
            'type': order.order_type.upper(),
            'price': order.price if order.order_type == 'limit' else None,
            'stop_price': order.stop_loss,
            'time_in_force': 'GTC'
        }
        
        response = await self._request('POST', '/v2/orders', data)
        
        return OrderResponse(
            order_id=response['id'],
            symbol=response['symbol'],
            side=response['side'].lower(),
            quantity=float(response['size']),
            price=float(response['price']),
            status=response['status'].lower(),
            timestamp=datetime.fromtimestamp(response['created_at'] / 1000)
        )
        
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order on Delta Exchange."""
        try:
            await self._request('DELETE', f'/v2/orders/{order_id}')
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            return False
            
    async def get_positions(self) -> List[Position]:
        """Get current positions from Delta Exchange."""
        response = await self._request('GET', '/v2/positions')
        positions = []
        
        for pos in response:
            if float(pos['size']) != 0:  # Only include non-zero positions
                position = Position(
                    symbol=pos['symbol'],
                    side='buy' if float(pos['size']) > 0 else 'sell',
                    quantity=abs(float(pos['size'])),
                    entry_price=float(pos['entry_price']),
                    current_price=float(pos['mark_price']),
                    unrealized_pnl=float(pos['unrealized_pnl']),
                    timestamp=datetime.fromtimestamp(pos['updated_at'] / 1000)
                )
                positions.append(position)
                
        return positions
        
    async def update_position(self, symbol: str, current_price: float) -> None:
        """Update position with current market price."""
        positions = await self.get_positions()
        for position in positions:
            if position.symbol == symbol:
                position.current_price = current_price
                position.unrealized_pnl = self.calculate_pnl(position, current_price)
                
                # Check trailing stop loss
                if await self.check_trailing_stop(symbol, current_price):
                    await self.close_position(symbol)
                    logger.info(f"Trailing stop loss triggered for {symbol}")
                break
                
    async def close_position(self, symbol: str) -> Optional[OrderResponse]:
        """Close position on Delta Exchange."""
        positions = await self.get_positions()
        position = next((p for p in positions if p.symbol == symbol), None)
        
        if position is None:
            return None
            
        close_order = OrderRequest(
            symbol=symbol,
            side='sell' if position.side == 'buy' else 'buy',
            quantity=position.quantity,
            order_type='market'
        )
        
        return await self.place_order(close_order)
        
    async def __del__(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
