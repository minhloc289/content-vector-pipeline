import requests
import time
from datetime import datetime
from ..config import BASE_URL, setup_logging, TIME_SLEEP_IN_SECONDS

# Configure logging for the fetcher module
logger = setup_logging()

def fetch_articles(per_page=10):
    """
    Fetch all articles from the OptiSigns support API.

    This function retrieves articles from the specified API endpoint, paginating through the results
    until there are no more pages to fetch. It includes a 2-second sleep after every 20 articles to avoid IP banning.

    Args:
        per_page (int): The number of articles to fetch per API request. Defaults to 10.

    Returns:
        list: A list of all article dictionaries fetched from the API.
    """
    start_time = datetime.now()
    logger.info(f"[Fetcher] Starting article fetch at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"[Fetcher] Fetching articles, {per_page} per page")

    url = f"{BASE_URL}?per_page={per_page}"
    articles = []
    page_count = 0
    article_count = 0

    while url:
        page_count += 1
        
        try:
            logger.debug(f"[Fetcher] Requesting page {page_count}")
            
            # Make the API request
            response = requests.get(url)
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()
            page_articles = data.get('articles', [])
            
            # Extend the articles list with the fetched articles
            articles.extend(page_articles)
            article_count += len(page_articles)
            logger.debug(f"[Fetcher] Page {page_count}: Retrieved {len(page_articles)} articles, Total: {article_count}")

            # Sleep for 2 seconds after every 20 articles
            if article_count >= 20 and article_count % 20 == 0:
                logger.debug(f"[Fetcher] Processed {article_count} articles, sleeping for 2 seconds")
                time.sleep(TIME_SLEEP_IN_SECONDS)

            # Get the next page URL
            url = data.get('next_page')


            if not url:
                logger.debug("[Fetcher] No more pages available")
                break

        except requests.exceptions.RequestException as e:
            logger.error(f"[Fetcher] API request failed on page {page_count}: {e}")
            break
        except Exception as e:
            logger.error(f"[Fetcher] Unexpected error on page {page_count}: {e}")
            break

    # Calculate execution time
    end_time = datetime.now()
    execution_time = end_time - start_time
    
    # Log summary
    logger.info(f"[Fetcher] Fetch completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"[Fetcher] Execution time: {execution_time.total_seconds():.2f} seconds")
    logger.info(f"[Fetcher] Results: {len(articles)} articles retrieved from {page_count} pages")
    
    return articles