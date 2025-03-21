# Autonomous Crypto Trading Bot

A sophisticated cryptocurrency trading bot with support for paper trading and live trading on Delta Exchange, featuring a modern web-based dashboard for monitoring and control.

## Features

- **Dual Trading Modes**
  - Paper Trading: Practice trading with simulated money
  - Live Trading: Real trading with actual funds
  
- **Advanced Risk Management**
  - Trailing Stop Loss
  - Position Size Management
  - Maximum Trade Size Limits
  
- **Delta Exchange Integration**
  - Real-time market data
  - Order execution
  - Position tracking
  
- **Modern Web Dashboard**
  - Real-time price charts
  - Position monitoring
  - Performance tracking
  - Configuration management
  
- **Safety Features**
  - Configurable risk parameters
  - Emergency stop functionality
  - Error handling and logging
  - API key validation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd autonomous-trading-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the bot:
- Copy `config.json` and update with your settings
- Set your Delta Exchange API keys if using live trading

## Configuration

The bot is configured through `config/config.json`:

```json
{
  "trading_mode": "paper",  // "paper" or "live"
  "exchange": {
    "name": "delta",
    "apiKey": "",          // Your Delta Exchange API key
    "secret": "",          // Your Delta Exchange API secret
    "testnet": true        // Use testnet for testing
  },
  "trading_pair": "BTC-USDT",
  "risk_management": {
    "stop_loss": {
      "type": "trailing",
      "activation_percent": 1.0,
      "trail_percent": 0.5
    },
    "position_size": {
      "max_trade_size": 0.01,
      "max_leverage": 10
    }
  }
}
```

## Usage

1. Start the bot:
```bash
python main.py
```

2. Access the dashboard:
- Open your browser and navigate to `http://localhost:8000`
- The dashboard will show real-time trading information and controls

## Dashboard Features

- **Real-time Monitoring**
  - Current positions and balances
  - Price charts and market data
  - PnL tracking
  
- **Trading Controls**
  - Start/Stop trading
  - Switch between paper/live modes
  - Configure trading parameters
  
- **Risk Management**
  - Set trailing stop-loss parameters
  - Configure position sizes
  - Set maximum trade limits

## Safety Guidelines

1. **Paper Trading First**
   - Always test strategies with paper trading before live trading
   - Verify bot behavior and performance in simulation

2. **API Security**
   - Use API keys with minimum required permissions
   - Never share or commit API keys
   - Regularly rotate API keys

3. **Risk Management**
   - Start with small position sizes
   - Use stop-loss protection
   - Monitor bot performance regularly

## Error Handling

The bot includes comprehensive error handling:

- Network connectivity issues
- API failures
- Invalid configurations
- Order execution errors

All errors are logged to `logs/trading_bot_[timestamp].log`

## Development

### Project Structure
```
autonomous-trading-bot/
├── backend/
│   ├── exchange/
│   │   ├── base.py
│   │   ├── delta.py
│   │   └── paper_trade.py
│   ├── trading_bot.py
│   └── logger.py
├── config/
│   └── config.json
├── ui/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── main.py
└── requirements.txt
```

### Adding New Features

1. **New Exchange Integration**
   - Create new exchange class in `backend/exchange/`
   - Implement BaseExchange interface
   - Add exchange-specific logic

2. **New Trading Strategies**
   - Modify trading logic in `trading_bot.py`
   - Implement strategy in isolated class
   - Add strategy parameters to configuration

3. **UI Enhancements**
   - Modify `ui/index.html` for layout changes
   - Update `ui/script.js` for new functionality
   - Style changes in `ui/style.css`

## Troubleshooting

Common issues and solutions:

1. **Connection Issues**
   - Verify internet connectivity
   - Check API key permissions
   - Ensure Delta Exchange is accessible

2. **Trading Issues**
   - Verify sufficient balance
   - Check position limits
   - Review error logs

3. **Dashboard Issues**
   - Clear browser cache
   - Check browser console for errors
   - Verify WebSocket connection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details

## Disclaimer

This bot is for educational purposes only. Cryptocurrency trading carries significant risks. Use at your own risk and never trade with money you cannot afford to lose.
