import requests

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
    BASE_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
    url = f"{BASE_URL}?per_page={per_page}"
    articles = []

    while url and len(articles) < limit:
        try:
            # Make the API request
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse the JSON response
            data = response.json()

            # Extend the articles list with the fetched articles
            articles.extend(data.get('articles', []))

            # Get the next page URL
            url = data.get('next_page')

        except requests.exceptions.RequestException as e:
            # Log the exception and break the loop
            print(f"Failed to fetch articles: {e}")
            break

    # Return the fetched articles, up to the specified limit
    return articles[:limit]