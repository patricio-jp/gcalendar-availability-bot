import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class CalendarChecker:
    def __init__(self, url):
        self.url = url
        self.driver = None

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run invisible
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920,1080")
        # Add User-Agent to look less like a bot
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def check_availability(self):
        """
        Scrapes the calendar page and returns a list of formatted slot strings (Date + Time).
        """
        if not self.driver:
            self._setup_driver()
        
        formatted_slots = []
        try:
            logger.info(f"Navigating to {self.url}...")
            self.driver.get(self.url)
            
            # Wait for the main grid or list to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Allow some time for dynamic JS to render the slots
            import time
            time.sleep(5)

            # Find all day containers (div[role='list'])
            # Each represents a column/day and has an aria-label with the full date
            day_lists = self.driver.find_elements(By.CSS_SELECTOR, "div[role='list']")
            
            for day in day_lists:
                date_label = day.get_attribute("aria-label") # e.g., "Jueves, 19 de febrero de 2026"
                if not date_label:
                    continue
                
                # Find slots within this day
                buttons = day.find_elements(By.CSS_SELECTOR, "div[role='listitem'] button")
                
                for btn in buttons:
                    try:
                        if btn.is_enabled():
                            time_label = btn.get_attribute("aria-label")
                            if not time_label:
                                time_label = btn.text
                            
                            if time_label:
                                # Clean up time label if it contains extra text (sometimes aria-label is verbose)
                                # Assuming standard format like "19:00" or simple text.
                                formatted_slots.append(f"🗓️ *{date_label}* — ⏰ {time_label}")
                    except Exception:
                        continue

            logger.info(f"Found {len(formatted_slots)} potential slots.")
            
        except Exception as e:
            logger.error(f"Selenium error: {e}")
            return []
        
        return formatted_slots

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
