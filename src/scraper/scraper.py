import os
import json
import shutil
from .fetcher import fetch_articles
from .converter import convert_article_to_markdown

def save_article_as_markdown(article):
    """
    Save an article as a Markdown file and metadata JSON file.

    This function takes an article dictionary, converts it to Markdown, and saves it as
    <article_id>.md in a subdirectory articles/<article_id>/. It also saves the article
    dictionary as metadata.json in the same subdirectory.

    Args:
        article (dict): The article dictionary containing at least 'id', 'title', 'body', and 'html_url'.
    """
    article_id = article.get('id')
    if article_id is None:
        print("Article has no id, skipping.")
        return

    try:
        # Create article subdirectory
        article_id_str = str(article_id)
        article_dir = os.path.join("articles", article_id_str)
        os.makedirs(article_dir, exist_ok=True)

        # Save Markdown file
        markdown_content = convert_article_to_markdown(article)
        markdown_path = os.path.join(article_dir, f"{article_id_str}.md")
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Save metadata JSON file
        metadata_path = os.path.join(article_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(article, f, indent=4)

        print(f"Saved article {article_id} to {article_dir}")
    except Exception as e:
        print(f"Failed to save article {article_id}: {e}")

def main():
    """
    Fetch articles and save them as Markdown files.

    This function checks if there are 50 or more article subdirectories in the 'articles'
    directory. If so, it clears the directory before fetching and saving new articles.
    It fetches up to 50 articles and saves each one using save_article_as_markdown.
    """
    try:
        # Check if articles directory exists and count subdirectories
        articles_dir = "articles"
        if os.path.exists(articles_dir):
            subdirs = [d for d in os.listdir(articles_dir) if os.path.isdir(os.path.join(articles_dir, d))]
            if len(subdirs) >= 50:
                print(f"Found {len(subdirs)} article directories, clearing {articles_dir}")
                shutil.rmtree(articles_dir)
                os.makedirs(articles_dir, exist_ok=True)
                print(f"Recreated {articles_dir}")

        # Fetch and save articles
        articles = fetch_articles(limit=50)
        for article in articles:
            save_article_as_markdown(article)
        print(f"Saved {len(articles)} articles to ./articles directory")
    except Exception as e:
        print(f"Failed to complete the scraping process: {e}")

if __name__ == "__main__":
    main()