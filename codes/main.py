import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.bot.telegram_bot import CampusCopilotBot
from src.nlp.nlp_processor import NLPProcessor

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    # Initialize NLP Processor
    nlp_processor = NLPProcessor()
    
    # Test NLP Processor
    test_queries = [
        "What is my schedule for tomorrow?",
        "Show me upcoming events this week",
        "Remind me to submit my essay at 5 PM today",
        "Where is the main library?",
        "How do I get to the computer science building?",
        "Summarize this article for me",
        "Create a poster for the spring festival",
        "Hello bot",
        "Thanks for your help",
        "I need help with something else"
    ]
    
    logger.info("\n--- Testing NLP Processor ---")
    for query in test_queries:
        result = nlp_processor.process_query(query)
        logger.info(f"Query: {query}")
        logger.info("  Intent: {}".format(result["intent"]))
        logger.info("  Entities: {}".format(result["entities"]))

    logger.info("--- NLP Processor Test Complete ---\n")

    # Initialize and run the Telegram bot
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file. Please set it.")
        return

    bot = CampusCopilotBot(telegram_bot_token)
    await bot.start_bot()

if __name__ == "__main__":
    asyncio.run(main())

