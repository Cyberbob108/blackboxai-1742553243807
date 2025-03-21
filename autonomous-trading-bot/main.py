import asyncio
import json
from aiohttp import web
from pathlib import Path
from backend.trading_bot import TradingBot
from backend.logger import logger

# Global variable declaration
bot = None

# Web Routes
async def index(request):
    """Serve the main dashboard page."""
    return web.FileResponse('ui/index.html')

async def start_bot(request):
    """Start the trading bot."""
    global bot
    try:
        if bot.is_running:
            return web.json_response({"status": "error", "message": "Bot is already running"})
        
        await bot.start()
        return web.json_response({"status": "success", "message": "Bot started"})
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def stop_bot(request):
    """Stop the trading bot."""
    global bot
    try:
        if not bot.is_running:
            return web.json_response({"status": "error", "message": "Bot is not running"})
        
        await bot.stop()
        return web.json_response({"status": "success", "message": "Bot stopped"})
    except Exception as e:
        logger.error(f"Error stopping bot: {str(e)}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def get_status(request):
    """Get current bot status."""
    global bot
    try:
        status = await bot.get_status()
        return web.json_response(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return web.json_response({
            "status": "error",
            "message": str(e),
            "is_running": bot.is_running if bot else False,
            "mode": "paper",
            "balances": {"USDT": 0.00, "BTC": 0.00000000, "total": 0.00},
            "positions": [],
            "total_pnl": 0.00
        }, status=500)

async def update_config(request):
    """Update bot configuration."""
    global bot
    try:
        data = await request.json()
        
        # Update config file
        config_path = Path('config/config.json')
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Restart bot if it was running
        was_running = bot.is_running
        if was_running:
            await bot.stop()
            
        # Reinitialize bot with new config
        bot = TradingBot()
        
        if was_running:
            await bot.start()
            
        return web.json_response({"status": "success", "message": "Configuration updated"})
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

def setup_routes(app):
    """Setup web application routes."""
    app.router.add_get('/', index)
    app.router.add_static('/ui', 'ui')  # Serve UI files
    app.router.add_post('/api/start', start_bot)
    app.router.add_post('/api/stop', stop_bot)
    app.router.add_get('/api/status', get_status)
    app.router.add_post('/api/config', update_config)

    # Add CORS middleware
    app.router.add_options('/{tail:.*}', handle_options_request)

async def handle_options_request(request):
    """Handle CORS preflight requests."""
    return web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400',
    })

@web.middleware
async def cors_middleware(request, handler):
    """CORS middleware to handle CORS headers for all responses."""
    if request.method == 'OPTIONS':
        return await handle_options_request(request)
    
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

async def init_app():
    """Initialize the web application."""
    global bot
    app = web.Application(middlewares=[cors_middleware])
    setup_routes(app)
    
    # Initialize bot
    bot = TradingBot()
    
    return app

def main():
    """Main entry point."""
    try:
        app = asyncio.run(init_app())
        web.run_app(app, host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == '__main__':
    main()
