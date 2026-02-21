import os
import time
import random
import signal
import logging
import logging.handlers
from dotenv import load_dotenv
from browser import CalendarChecker
from notifier import TelegramNotifier

# Setup logging with rotation so the log file never grows unbounded
load_dotenv()

rotating_handler = logging.handlers.RotatingFileHandler(
    "bot.log", maxBytes=5 * 1024 * 1024, backupCount=3  # 5 MB per file, keep 3 backups
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[rotating_handler, logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def job(checker: CalendarChecker, notifier: TelegramNotifier, url: str):
    """
    Main job to check calendar availability and notify if slots are found.
    Receives shared instances to avoid creating a new browser on every call.
    """
    logger.info("Starting scheduled check...")
    try:
        available_slots = checker.check_availability()
        if available_slots:
            message = "📅 *New Slots Available!*\n\n" + "\n".join(available_slots)
            message += f"\n\n[Book Here]({url})"
            notifier.send_message(message)
            logger.info(f"Notification sent for {len(available_slots)} slots.")
        else:
            logger.info("No slots found.")
    except Exception as e:
        logger.error(f"Error during check: {e}")


def run_scheduler():
    """
    Runs the availability check with a randomised interval to avoid detection.
    A single CalendarChecker (and thus a single browser session) is shared across
    all checks, restarted periodically inside the checker itself.
    """
    load_dotenv(override=True)

    url = os.getenv("CALENDAR_URL")
    if not url or "your_" in url:
        logger.error("CALENDAR_URL not set correctly in .env – aborting.")
        return

    min_interval = int(os.getenv("CHECK_INTERVAL_MIN", 5))
    max_interval = int(os.getenv("CHECK_INTERVAL_MAX", 10))

    logger.info(f"Bot started. Check interval: {min_interval}-{max_interval} minutes.")

    # Create shared instances once – the browser stays alive across checks
    checker = CalendarChecker(url)
    notifier = TelegramNotifier()

    # Graceful shutdown: close the browser properly on SIGTERM / SIGINT
    def _shutdown(signum, frame):
        logger.info("Shutdown signal received – closing browser.")
        checker.close()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        # Run once immediately on start
        job(checker, notifier, url)

        while True:
            interval = random.randint(min_interval * 60, max_interval * 60)
            logger.info(
                f"Sleeping for {interval // 60} min {interval % 60} sec..."
            )
            time.sleep(interval)
            job(checker, notifier, url)
    finally:
        checker.close()


if __name__ == "__main__":
    run_scheduler()
