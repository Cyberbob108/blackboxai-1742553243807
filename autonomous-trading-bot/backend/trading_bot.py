import asyncio
import json
from datetime import datetime
from pathlib import Path
import random
from collections import namedtuple

from .logger import logger
from .exchange.paper_trade import PaperTradingExchange
from .exchange.delta import DeltaExchange

class TradingBot:
    def __init__(self):
        """Initialize the trading bot."""
        self.config = self._load_config()
        self.is_running = False
        self.last_trade = None
        
        # Initialize exchange
        if self.config.get('paper_trading', True):
            self.exchange = PaperTradingExchange(config=self.config)
            logger.info("Initializing paper trading exchange")
        else:
            self.exchange = DeltaExchange(
                api_key=self.config['api_key'],
                api_secret=self.config['api_secret'],
                config=self.config
            )
            logger.info("Initializing live trading exchange")
            
    def _load_config(self):
        """Load configuration from config.json."""
        try:
            config_path = Path('config/config.json')
            with open(config_path) as f:
                config = json.load(f)
            
            # Add default risk management settings if not present
            if 'risk_management' not in config:
                config['risk_management'] = {
                    'position_size': {'max_trade_size': 1.0},
                    'stop_loss': {
                        'type': 'trailing',
                        'activation_percent': 1.0,
                        'trail_percent': 0.5
                    }
                }
            
            return config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            # Return default config
            return {
                'paper_trading': True,
                'trading_pair': 'BTC-USDT',
                'order_size': 0.01,
                'risk_management': {
                    'position_size': {'max_trade_size': 1.0},
                    'stop_loss': {
                        'type': 'trailing',
                        'activation_percent': 1.0,
                        'trail_percent': 0.5
                    }
                }
            }
            
    async def start(self):
        """Start the trading bot."""
        if self.is_running:
            return
            
        try:
            # Connect to exchange
            await self.exchange.connect()
            logger.info("Paper trading exchange connected")
            
            self.is_running = True
            logger.info("Trading bot started")
            
            # Execute initial trade
            await self._execute_trade()
            
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            raise
            
    async def stop(self):
        """Stop the trading bot."""
        if not self.is_running:
            return
            
        self.is_running = False
        logger.info("Trading bot stopped")
        
    async def get_status(self):
        """Get current bot status."""
        try:
            balances = await self.exchange.get_balance()
            positions = await self.exchange.get_positions()
            
            # Calculate total PnL
            total_pnl = 0
            for position in positions:
                if isinstance(position, dict) and 'pnl' in position:
                    total_pnl += float(position['pnl'])
            
            return {
                'is_running': self.is_running,
                'mode': 'paper' if isinstance(self.exchange, PaperTradingExchange) else 'live',
                'status': 'running' if self.is_running else 'stopped',
                'balances': {
                    'USDT': round(float(balances.get('USDT', 0)), 2),
                    'BTC': round(float(balances.get('BTC', 0)), 8),
                    'total': round(float(balances.get('total', 0)), 2)
                },
                'positions': [
                    {
                        'symbol': p['symbol'],
                        'quantity': round(float(p['quantity']), 8),
                        'entry_price': round(float(p['entry_price']), 2),
                        'current_price': round(float(p['current_price']), 2),
                        'pnl': round(float(p['pnl']), 2)
                    } for p in positions
                ],
                'total_pnl': round(total_pnl, 2),
                'last_trade': {
                    'order_id': self.last_trade.order_id,
                    'symbol': self.last_trade.symbol,
                    'side': self.last_trade.side,
                    'quantity': round(float(self.last_trade.quantity), 8),
                    'price': round(float(self.last_trade.price), 2),
                    'status': self.last_trade.status,
                    'timestamp': self.last_trade.timestamp.isoformat()
                } if self.last_trade else None
            }
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {
                'is_running': self.is_running,
                'mode': 'paper' if isinstance(self.exchange, PaperTradingExchange) else 'live',
                'status': 'running' if self.is_running else 'stopped',
                'balances': {'USDT': 0.00, 'BTC': 0.00000000, 'total': 0.00},
                'positions': [],
                'total_pnl': 0.00,
                'last_trade': None,
                'error': str(e)
            }
        
    async def _execute_trade(self):
        """Execute a trade based on strategy."""
        try:
            # Simple example: place a buy order
            symbol = self.config.get('trading_pair', 'BTC-USDT')
            quantity = self.config.get('order_size', 0.01)
            
            self.last_trade = await self.exchange.place_order(
                symbol=symbol,
                side='buy',
                quantity=quantity
            )
            
            logger.info(f"Entry order placed: {self.last_trade}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            raise
