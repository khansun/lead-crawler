from utils.csv_writer import CSVWriter
from scraper.trustpilot import TrustpilotScraper

platforms = [
    {"url": "https://www.trustpilot.com/review/octopus.energy", "platform_name": "Octopus Energy"},
    {"url": "https://www.trustpilot.com/review/themoneyplatform.com", "platform_name": "The Money Platform"},
    {"url": "https://www.trustpilot.com/review/triodos.co.uk", "platform_name": "Triodos Bank UK"},
    {"url": "https://www.trustpilot.com/review/yielders.co.uk", "platform_name": "Yielders"},
    {"url": "https://www.trustpilot.com/review/simplecrowdfunding.co.uk", "platform_name": "Simple Crowdfunding"},
    {"url": "https://www.trustpilot.com/review/uown.co", "platform_name": "UOWN"},
]

for platform in platforms:
    print(f"[INFO] Scraping leads from: {platform['platform_name']}")
    scraper = TrustpilotScraper(
        url=platform["url"],
        platform_name=platform["platform_name"]
    )
    scraper.setup_driver()
    leads = scraper.scrape_leads()
    print(f"[INFO] Found {len(leads)} leads from {platform['platform_name']}")
    
    csv_file = f"csv/{platform['platform_name'].lower().replace(' ', '_')}.csv"
    csv_writer = CSVWriter(csv_file)
    for lead in leads:
        csv_writer.write_row(lead)
    csv_writer.close()
    scraper.close()
