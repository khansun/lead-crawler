from scraper.property118_scraper import Property118Scraper
from utils.csv_writer import CSVWriter
def main():
    url = "https://www.property118.com/is-it-time-to-change-the-narrative/"
    scraper = Property118Scraper(url)
    csv_writer = CSVWriter("csv/property118comments.csv")
    try:
        scraper.setup_driver()
        comments = scraper.scrape_comments()
        for comment in comments:
            csv_writer.write_row(comment)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        csv_writer.close()
        scraper.close()

if __name__ == "__main__":
    main()
