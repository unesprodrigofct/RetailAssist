#!/usr/bin/env python3
"""Script to run the RetailAssist Telegram Bot."""

import sys
from retail_assist.bot.telegram_bot import RetailAssistBot
from retail_assist.infra.settings import settings
from retail_assist.infra.logging import logger

def main():
    """Main function to run the bot."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is required. Please set it in your .env file.")
        logger.info("To get a token:")
        logger.info("1. Open Telegram and search for @BotFather")
        logger.info("2. Send /newbot and follow the instructions")
        logger.info("3. Copy the token to your .env file")
        sys.exit(1)
    
    logger.info("Starting RetailAssist Telegram Bot...")
    logger.info(f"OpenAI integration: {'Enabled' if settings.OPENAI_API_KEY else 'Disabled (using fallback responses)'}")
    
    bot = RetailAssistBot()
    
    try:
        if settings.TELEGRAM_WEBHOOK_URL:
            logger.info(f"Running bot with webhook: {settings.TELEGRAM_WEBHOOK_URL}")
            # For webhook, we'd need async setup - for now just polling
            logger.info("Webhook mode not implemented yet, using polling...")
            
        logger.info("Running bot with polling...")
        
        # Setup and run the bot
        application = bot.setup_bot()
        application.run_polling(drop_pending_updates=True)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
