import os
import time
import random
import logging
from dotenv import load_dotenv
import schedule
from browser import CalendarChecker
from notifier import TelegramNotifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def job():
    """
    Main job to check calendar and notify if slots are found.
    """
    logger.info("Starting scheduled check...")
    
    # Reload env vars in case they change without restart (optional, but good for testing)
    load_dotenv(override=True)
    
    url = os.getenv("CALENDAR_URL")
    if not url or "your_" in url:
        logger.warning("CALENDAR_URL not set correctly in .env")
        return

    checker = CalendarChecker(url)
    notifier = TelegramNotifier()
    
    try:
        available_slots = checker.check_availability()
        if available_slots:
            message = "📅 **New Slots Available!**\n\n" + "\n".join(available_slots)
            message += f"\n\n[Book Here]({url})"
            notifier.send_message(message)
            logger.info(f"Notification sent for {len(available_slots)} slots.")
        else:
            logger.info("No slots found.")
    except Exception as e:
        logger.error(f"Error during check: {e}")
    finally:
        checker.close()

def run_scheduler():
    """
    Runs the job with a randomized interval to avoid detection.
    """
    load_dotenv()
    min_interval = int(os.getenv("CHECK_INTERVAL_MIN", 5))
    max_interval = int(os.getenv("CHECK_INTERVAL_MAX", 10))
    
    logger.info(f"Bot started. Check interval: {min_interval}-{max_interval} minutes.")
    
    # Run once immediately on start
    job()
    
    while True:
        # Randomized wait
        interval = random.randint(min_interval * 60, max_interval * 60)
        logger.info(f"Sleeping for {interval // 60} minutes and {interval % 60} seconds...")
        time.sleep(interval)
        job()

if __name__ == "__main__":
    run_scheduler()
