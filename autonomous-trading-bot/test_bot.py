import asyncio
import json
from backend.trading_bot import TradingBot
from backend.logger import logger

async def test_paper_trading():
    """
    Test basic paper trading functionality.
    """
    try:
        # Initialize bot with test configuration
        bot = TradingBot()
        
        # Start the bot
        await bot.start()
        logger.info("Bot started successfully")
        
        # Get initial status
        status = await bot.get_status()
        logger.info(f"Initial status: {json.dumps(status, indent=2)}")
        
        # Wait for a few cycles
        logger.info("Waiting for trading cycles...")
        await asyncio.sleep(10)
        
        # Get updated status
        status = await bot.get_status()
        logger.info(f"Updated status: {json.dumps(status, indent=2)}")
        
        # Stop the bot
        await bot.stop()
        logger.info("Bot stopped successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting paper trading test...")
    
    # Run the test
    success = asyncio.run(test_paper_trading())
    
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed! Check the logs for details.")
