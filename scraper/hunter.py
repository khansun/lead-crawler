import csv
import requests
import time
import logging
import pandas as pd
import os
from typing import Optional
from tqdm import tqdm
class HunterScraper:
    def __init__(self, domain: str, api_key: Optional[str] = None, sleep_seconds: float = 1.5):
        self.domain = domain
        self.sleep_seconds = sleep_seconds
        self.api_key = api_key or os.getenv("HUNTER_API_KEY")
        
        if not self.api_key:
            raise EnvironmentError("HUNTER_API_KEY not set in environment or constructor")

        logging.basicConfig(
            filename='hunter.log',
            level=logging.INFO,
            format='[%(levelname)s] %(asctime)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def clean_csv(self, input_path: str) -> list[dict]:
        df = pd.read_csv(input_path)
        df_cleaned = df.drop_duplicates(subset='Name', keep='first')
        df_cleaned.to_csv(input_path, index=False)
        self.logger.info(f"Cleaned CSV saved to: {input_path}")
        return df_cleaned.to_dict(orient='records')

    def find_email(self, name: str) -> Optional[str]:
        url = 'https://api.hunter.io/v2/email-finder'
        params = {
            'domain': self.domain,
            'full_name': name,
            'api_key': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            email = data.get('data', {}).get('email')
            if email:
                self.logger.info(f"Found email for {name}: {email}")
            else:
                self.logger.info(f"No email found for {name}")
            return email
        except Exception as e:
            self.logger.error(f"Error fetching email for {name}: {e}")
            return None

    def enrich_emails(self, input_path: str, output_path: str):
        if not os.path.exists(input_path):
            self.logger.error(f"Input file not found: {input_path}")
            return

        rows = self.clean_csv(input_path)
        if not rows:
            self.logger.warning("No rows to process after cleaning.")
            return

        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Name", "Email", "Source URL", "Platform"])

            for row in tqdm(rows, desc="Find Email", unit="row"):
                name = row.get('Name', '').strip()
                company = row.get('Platform', '').strip()
                source_url = row.get("Source URL", "").strip()

                if not name:
                    writer.writerow([name, "", source_url, company])
                    continue

                self.logger.info(f"Searching for {name} at {self.domain}")
                email = self.find_email(name) or ""
                writer.writerow([name, email, source_url, company])
                time.sleep(self.sleep_seconds)
