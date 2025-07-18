import os
import json
import hashlib
from datetime import datetime
from .fetcher import fetch_articles
from .converter import convert_article_to_markdown

def calculate_content_hash(content):
    """
    Calculate SHA-256 hash of the given content.

    Args:
        content (str): Content to hash.

    Returns:
        str: Hexadecimal SHA-256 hash.
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def load_tracked_metadata():
    """
    Load the tracked metadata from articles_metadata.json.

    Returns:
        dict: Dictionary of article_id -> metadata.
    """
    metadata_path = "articles_metadata.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tracked_metadata(tracked_metadata):
    """
    Save the tracked metadata to articles_metadata.json.

    Args:
        tracked_metadata (dict): Dictionary of article_id -> metadata.
    """
    metadata_path = "articles_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(tracked_metadata, f, indent=4)

def save_article_as_markdown(article, tracked_metadata):
    """
    Save an article as a Markdown file and metadata JSON file if it's new or updated.

    This function checks if the article is new or has changed by comparing its content hash
    with the stored metadata. If it is new or updated, it saves the Markdown and metadata files.

    Args:
        article (dict): The article dictionary containing at least 'id', 'title', 'body', and 'html_url'.
        tracked_metadata (dict): Dictionary of tracked article metadata.

    Returns:
        tuple: (bool, str, str) - Whether saved (True/False), status ('new', 'updated', or 'skipped'),
               article ID (or None if not saved).
    """
    article_id = article.get('id')
    if article_id is None:
        print("Article has no id, skipping.")
        return False, 'skipped', None

    try:
        # Calculate content hash
        content = article.get('body', '')
        content_hash = calculate_content_hash(content)
        article_id_str = str(article_id)
        last_modified = article.get('updated_at', datetime.utcnow().isoformat())

        # Check if article is new or updated
        status = 'skipped'
        if article_id_str not in tracked_metadata:
            print(f"New article detected: {article_id}")
            status = 'new'
        elif tracked_metadata[article_id_str]['content_hash'] != content_hash:
            print(f"Updated article detected: {article_id}")
            status = 'updated'

        if status == 'skipped':
            print(f"No changes for article {article_id}, skipping.")
            return False, status, None

        # Create article subdirectory
        article_dir = os.path.join("articles", article_id_str)
        os.makedirs(article_dir, exist_ok=True)

        # Save Markdown file
        markdown_content = convert_article_to_markdown(article)
        markdown_path = os.path.join(article_dir, f"{article_id_str}.md")
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Save metadata JSON file
        metadata = {
            'id': article_id,
            'title': article.get('title', 'No Title'),
            'html_url': article.get('html_url', ''),
            'content_hash': content_hash,
            'last_modified': last_modified
        }
        metadata_path = os.path.join(article_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        # Update tracked metadata
        tracked_metadata[article_id_str] = {
            'content_hash': content_hash,
            'last_modified': last_modified
        }
        print(f"Saved article {article_id} to {article_dir}")
        return True, status, article_id_str

    except Exception as e:
        print(f"Failed to save article {article_id}: {e}")
        return False, 'skipped', None

def main():
    """
    Fetch articles, save new or updated ones as Markdown files, and return IDs of affected articles.

    This function loads existing metadata, fetches articles, saves only new or updated
    articles, reports the number of new and updated articles, and returns their IDs as an object.

    Returns:
        dict: Dictionary with 'newArticles' (set of new article IDs) and 'updatedArticles' (set of updated article IDs).
    """
    try:
        # Ensure articles directory exists
        articles_dir = "articles"
        os.makedirs(articles_dir, exist_ok=True)

        # Load tracked metadata
        tracked_metadata = load_tracked_metadata()
        print(f"Loaded metadata for {len(tracked_metadata)} articles")

        # Fetch articles
        articles = fetch_articles(limit=70, per_page=10)
        new_count = 0
        updated_count = 0
        delta_articles = {"newArticles": set(), "updatedArticles": set()}

        # Process articles
        for article in articles:
            saved, status, article_id = save_article_as_markdown(article, tracked_metadata)
            if saved:
                if status == 'new':
                    new_count += 1
                    delta_articles["newArticles"].add(article_id)
                elif status == 'updated':
                    updated_count += 1
                    delta_articles["updatedArticles"].add(article_id)

        # Save updated tracked metadata
        save_tracked_metadata(tracked_metadata)
        print(f"Processed {len(articles)} articles, saved {new_count} new and {updated_count} updated articles")
        if delta_articles["newArticles"] or delta_articles["updatedArticles"]:
            print(f"New or updated article IDs: newArticles: {{{', '.join(delta_articles['newArticles'])}}}, updatedArticles: {{{', '.join(delta_articles['updatedArticles'])}}}")
        else:
            print("No new or updated articles")

        return delta_articles

    except Exception as e:
        print(f"Failed to complete the scraping process: {e}")
        return {"newArticles": set(), "updatedArticles": set()}
if __name__ == "__main__":
    main()