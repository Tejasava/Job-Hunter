#!/usr/bin/env python3
"""
Main Entry Point - Start the Telegram Bot
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    try:
        from backend.telegram.telegram_bot import main as bot_main
        
        logger.info("Starting AI Job Hunter Agent")
        logger.info("=" * 50)
        
        await bot_main()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Please install required dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.warning("Continuing with basic bot mode...")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check for required environment variables
    from dotenv import load_dotenv
    
    # Load from config/.env
    env_path = Path(__file__).parent / "config" / ".env"
    load_dotenv(dotenv_path=env_path)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        logger.error(f"Please add your Telegram bot token to {env_path}")
        sys.exit(1)
    
    logger.info("✅ Configuration loaded successfully")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("✅ Bot stopped gracefully")
