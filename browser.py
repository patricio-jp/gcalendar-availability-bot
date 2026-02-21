import shutil
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

logger = logging.getLogger(__name__)

# Restart the browser every N checks to prevent gradual memory accumulation
RESTART_EVERY_N_CHECKS = 15


class CalendarChecker:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self._check_count = 0
        self._setup_driver()

    def _setup_driver(self):
        """Creates and configures a Chrome WebDriver instance."""
        self._teardown_driver()

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Use the newer headless implementation
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920,1080")
        # Reduce memory footprint
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--mute-audio")
        # Minimise disk cache growth inside the container
        chrome_options.add_argument("--disk-cache-size=1")
        chrome_options.add_argument("--media-cache-size=1")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.212 Safari/537.36"
        )

        # Locate system-installed browser and driver (works both in Docker and locally)
        browser_binary = (
            shutil.which("chromium")
            or shutil.which("chromium-browser")
            or shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
        )
        chromedriver_binary = shutil.which("chromedriver")

        if browser_binary:
            chrome_options.binary_location = browser_binary
            logger.info(f"Using browser at: {browser_binary}")

        if chromedriver_binary:
            service = Service(chromedriver_binary)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Fall back to Selenium Manager (bundled with Selenium 4.6+)
            logger.info("chromedriver not found in PATH – using Selenium Manager.")
            self.driver = webdriver.Chrome(options=chrome_options)

        self.driver.set_page_load_timeout(30)
        logger.info("Chrome WebDriver initialised.")

    def _teardown_driver(self):
        """Safely quits the current WebDriver instance."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error while quitting driver: {e}")
            finally:
                self.driver = None

    def _is_driver_alive(self) -> bool:
        """Returns True if the driver session is still responsive."""
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False

    def check_availability(self):
        """
        Scrapes the calendar page and returns a list of formatted slot strings (Date + Time).
        The WebDriver instance is reused across calls and restarted periodically.
        """
        self._check_count += 1

        # Proactively restart the browser every N checks to shed accumulated memory
        if self._check_count % RESTART_EVERY_N_CHECKS == 0:
            logger.info(f"Scheduled browser restart after {self._check_count} checks.")
            self._setup_driver()
        elif not self._is_driver_alive():
            logger.warning("Driver is unresponsive – reinitialising.")
            self._setup_driver()

        formatted_slots = []
        try:
            logger.info(f"Navigating to {self.url}...")
            self.driver.get(self.url)

            # Wait for the page body to be present
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Allow dynamic JS to render the booking slots
            time.sleep(5)

            # Each div[role='list'] represents a day column with an aria-label date
            day_lists = self.driver.find_elements(By.CSS_SELECTOR, "div[role='list']")

            for day in day_lists:
                date_label = day.get_attribute("aria-label")  # e.g. "Jueves, 19 de febrero de 2026"
                if not date_label:
                    continue

                buttons = day.find_elements(By.CSS_SELECTOR, "div[role='listitem'] button")

                for btn in buttons:
                    try:
                        if btn.is_enabled():
                            time_label = btn.get_attribute("aria-label") or btn.text
                            if time_label:
                                formatted_slots.append(f"🗓️ *{date_label}* — ⏰ {time_label}")
                    except Exception:
                        continue

            logger.info(f"Found {len(formatted_slots)} potential slots.")

        except WebDriverException as e:
            logger.error(f"WebDriver error: {e}")
            # Force re-initialisation on the next check
            self._teardown_driver()
        except Exception as e:
            logger.error(f"Unexpected error during check: {e}")

        return formatted_slots

    def close(self):
        """Permanently closes the browser (call on bot shutdown)."""
        self._teardown_driver()
        logger.info("Chrome WebDriver closed.")
