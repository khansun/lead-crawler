import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

logging.basicConfig(filename='trustpilot.log', level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

logger = logging.getLogger(__name__)


class TrustpilotScraper:
    def __init__(self, url: str, platform_name: str, timeout: int = 20, max_pagination: int = 10):
        self.url = url
        self.platform_name = platform_name
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.max_pagination = max_pagination

    def setup_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.timeout)

    def scroll_page(self, scroll_pause=1, max_scrolls=5):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logger.info("Reached bottom of page.")
                break
            last_height = new_height

    def scrape_leads_on_page(self):
        leads = []
        self.scroll_page(scroll_pause=3, max_scrolls=2)
        reviewers = self.driver.find_elements(By.CSS_SELECTOR, "aside.styles_consumerInfoWrapper__6HN5O")
        logger.info(f"Found {len(reviewers)} reviewers on this page.")
        for reviewer in reviewers:
            try:
                name = reviewer.find_element(By.CSS_SELECTOR, "a[data-consumer-profile-link='true'] span[data-consumer-name-typography='true']").text.strip()
                leads.append({
                    "Name": name,
                    "Email": "",
                    "Source URL": self.driver.current_url,
                    "Platform": self.platform_name
                })
            except Exception as e:
                logger.warning(f"Failed to extract reviewer: {e}")
                continue
        return leads

    def scrape_leads(self):
        logger.info(f"Starting scraping for {self.url}")
        self.driver.get(self.url)
        all_leads = []
        page = 1
        while page <= self.max_pagination:
            logger.info(f"Scraping page {page}")
            leads = self.scrape_leads_on_page()
            all_leads.extend(leads)
            if not self.click_next_page():
                logger.info("No next page. Scraping complete.")
                break
            page += 1
        return all_leads

    def click_next_page(self):
        try:
            next_link = self.driver.find_element(By.CSS_SELECTOR, "a[data-pagination-button-next-link='true']")
            if next_link.is_displayed():
                next_href = next_link.get_attribute("href")
                logger.info(f"Navigating to next page: {next_href}")
                self.driver.get(next_href)
                time.sleep(2)
                return True
            else:
                return False
        except Exception as e:
            logger.warning(f"No next page link found: {e}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
