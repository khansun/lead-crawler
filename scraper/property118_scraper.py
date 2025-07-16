from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Property118Scraper:
    def __init__(self, url: str, timeout: int = 20):
        self.url = url
        self.timeout = timeout
        self.driver = None
        self.wait = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.timeout)

    def scrape_comments(self):
        print(f"[INFO] Opening post: {self.url}")
        self.driver.get(self.url)

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.comment-block")))
        print("[INFO] Comments loaded")

        comments = self.driver.find_elements(By.CSS_SELECTOR, "div.comment-block")
        print(f"[INFO] Found {len(comments)} comments")

        all_comments = []
        for idx, comment_block in enumerate(comments, 1):
            try:
                commenter = comment_block.find_element(By.CSS_SELECTOR, ".comment-profile-pill p.fw-600").text.strip()
            except:
                commenter = "Unknown"

            try:
                paragraphs = comment_block.find_elements(By.CSS_SELECTOR, ".the-comment p")
                comment_text = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())
            except:
                comment_text = "[No text]"

            print(f"[COMMENT {idx}] {commenter}:\n{comment_text[:300]}")
            print("-" * 80)

            all_comments.append({
                "Name": commenter,
                "Email": "",  # try to extract email if available
                "Source URL": self.url,
                "Platform": "Property118"
            })
        return all_comments

    def close(self):
        if self.driver:
            self.driver.quit()

