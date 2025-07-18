import requests
from datetime import datetime
from ..config import BASE_URL, setup_logging

# Configure logging for the fetcher module
logger = setup_logging()

def fetch_articles(limit=50, per_page=10):
    """
    Fetch articles from the Optisigns support API.

    This function retrieves articles from the specified API endpoint, paginating through the results
    until the desired number of articles is reached or there are no more pages to fetch.

    Args:
        limit (int): The maximum number of articles to fetch. Defaults to 50.
        per_page (int): The number of articles to fetch per API request. Defaults to 10.

    Returns:
        list: A list of article dictionaries fetched from the API, up to the specified limit.
    """
    start_time = datetime.now()
    logger.info(f"[Fetcher] Starting article fetch at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"[Fetcher] Target: {limit} articles, {per_page} per page")

    url = f"{BASE_URL}?per_page={per_page}"
    articles = []
    page_count = 0

    while url and len(articles) < limit:
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
            logger.debug(f"[Fetcher] Page {page_count}: Retrieved {len(page_articles)} articles")

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
    
    # Return the fetched articles, up to the specified limit
    final_articles = articles[:limit]
    
    # Log summary
    logger.info(f"[Fetcher] Fetch completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"[Fetcher] Execution time: {execution_time.total_seconds():.2f} seconds")
    logger.info(f"[Fetcher] Results: {len(final_articles)} articles retrieved from {page_count} pages")
    
    if len(final_articles) < limit:
        logger.warning(f"[Fetcher] Retrieved fewer articles than requested ({len(final_articles)}/{limit})")

    return final_articles