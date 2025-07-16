from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

class TrustpilotScraper:
    def __init__(self, url: str, platform_name: str, timeout: int = 20):
        self.url = url
        self.platform_name = platform_name
        self.timeout = timeout
        self.driver = None
        self.wait = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")  # Hide webdriver flag

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.timeout)

    def scroll_page(self, scroll_pause=2, max_scrolls=10):
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for i in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)  # wait for loading

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("[INFO] Reached bottom of page, stopping scroll.")
                break  # no more content
            last_height = new_height
            print(f"[INFO] Scrolled to height: {last_height}")

    def click_load_more(self):
        try:
            load_more_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-service='load-more-reviews']")
            if load_more_button.is_displayed() and load_more_button.is_enabled():
                print("[INFO] Clicking 'Load more reviews' button...")
                load_more_button.click()
                time.sleep(3)  # wait for new reviews to load
                return True
            else:
                return False
        except:
            # No load more button found
            return False

    def scrape_leads(self):
        print(f"[INFO] Opening Trustpilot page: {self.url}")
        self.driver.get(self.url)

        # Scroll to bottom slowly to load content
        self.scroll_page(scroll_pause=2, max_scrolls=10)

        # Wait until at least one name element is present
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "aside.styles_consumerInfoWrapper__6HN5O")
            ))
        except Exception as e:
            print("[WARN] No reviewer names found:", e)
            return []
        leads = []
        # Find all asides with consumer info
        asides = self.driver.find_elements(By.CSS_SELECTOR, "aside.styles_consumerInfoWrapper__6HN5O")

        for aside in asides:
            try:
                name_span = aside.find_element(By.CSS_SELECTOR, "a[data-consumer-profile-link='true'] span[data-consumer-name-typography='true']")
                name = name_span.text.strip()
                
                leads.append({
                    "Name": name,
                    "Email": "email",
                    "Source URL": self.url,
                    "Platform": self.platform_name
                })
                
            except:
                continue


        return leads

    def close(self):
        if self.driver:
            self.driver.quit()
