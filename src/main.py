import requests

BASE_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json?per_page=10"

current_page = 1
max_page = 5
article_count = 0

with open("articles.txt", "w", encoding="utf-8") as file:
    url = BASE_URL

    while current_page <= max_page:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch page {current_page}")
            break

        data = response.json()
        articles = data.get('articles', [])

        for article in articles:
            title = article.get('title')
            html_url = article.get('html_url')
            line = f"Article: [{title}] - URL: [{html_url}]"
            print(line)
            file.write(line + "\n")
            article_count += 1

        # Update to next_page URL from response
        url = data.get('next_page')
        current_page += 1

        print(f"\nTổng số articles đã lưu: {article_count}")
