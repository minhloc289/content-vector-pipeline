from .scraper.scraper import main as scrape_main
from .uploader.upload import upload_delta_articles_in_batches
from .config import setup_logging

# Set up logging for the main module
logger = setup_logging()

def main():
    # Execute scraping to get delta articles
    # print("Starting article scraping...")
    logger.info("================ Starting article scraping ===============")
    articles = scrape_main()
    logger.info("================ Finished article scraping ===============\n")

    # Upload the delta articles
    logger.info("================ Starting article upload ================")
    upload_delta_articles_in_batches(articles)
    logger.info("================ Finished article upload ================\n")

if __name__ == "__main__":
    main()