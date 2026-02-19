import os
import requests
import logging

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, text):
        if not self.token or not self.chat_id:
            logger.warning("Telegram token or Chat ID missing.")
            return

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
