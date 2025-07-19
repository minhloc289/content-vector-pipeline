import os
import json
import hashlib
import re
from datetime import datetime
from .fetcher import fetch_articles
from .converter import convert_article_to_markdown
from ..config import setup_logging

# Configure logging for the scraper module
logger = setup_logging()

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
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                logger.info(f"[Scraper] Loaded existing metadata for {len(metadata)} articles")
                return metadata
        except Exception as e:
            logger.error(f"[Scraper] Failed to load metadata file: {e}")
            return {}
    else:
        logger.info("[Scraper] No existing metadata file found, starting fresh")
        return {}

def save_tracked_metadata(tracked_metadata):
    """
    Save the tracked metadata to articles_metadata.json.

    Args:
        tracked_metadata (dict): Dictionary of article_id -> metadata.
    """
    metadata_path = "articles_metadata.json"
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(tracked_metadata, f, indent=4)
        logger.debug(f"[Scraper] Metadata saved successfully")
    except Exception as e:
        logger.error(f"[Scraper] Failed to save metadata: {e}")

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
        logger.warning("[Scraper] Article missing ID, skipping")
        return False, 'skipped', None

    try:
        # Calculate content hash
        content = article.get('body', '')
        content_hash = calculate_content_hash(content)
        article_id_str = str(article_id)
        last_modified = article.get('updated_at', datetime.utcnow().isoformat())
        title = article.get('title', 'No Title')

        # Clean title by replacing punctuation with dashes
        clean_title = re.sub(r'[^\w\s-]', '-', title)  # Replace non-word characters with -
        clean_title = re.sub(r'\s+', '-', clean_title)  # Replace spaces with -
        clean_title = clean_title.strip('-')  # Remove leading/trailing dashes

        # Check if article is new or updated
        status = 'skipped'
        if article_id_str not in tracked_metadata:
            status = 'new'
        elif tracked_metadata[article_id_str]['content_hash'] != content_hash:
            status = 'updated'

        if status == 'skipped':
            logger.debug(f"[Scraper] Article {article_id} unchanged, skipping")
            return False, status, None

        # Create article subdirectory
        article_dir = os.path.join("articles", article_id_str)
        os.makedirs(article_dir, exist_ok=True)

        # Save Markdown file with cleaned title
        markdown_content = convert_article_to_markdown(article)
        markdown_path = os.path.join(article_dir, f"{clean_title}.md")
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Save metadata JSON file
        metadata = {
            'id': article_id,
            'title': title,
            'html_url': article.get('html_url', ''),
            'content_hash': content_hash,
            'last_modified': last_modified
        }
        metadata_path = os.path.join(article_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        # Update tracked metadata
        tracked_metadata[article_id_str] = {
            'clean_title': clean_title,
            'content_hash': content_hash,
            'last_modified': last_modified
        }
        
        logger.info(f"[Scraper] {status.capitalize()} article saved - ID: {article_id}, Title: '{title}'")
        return True, status, article_id_str

    except Exception as e:
        logger.error(f"[Scraper] Failed to save article {article_id}: {e}")
        return False, 'skipped', None

def main():
    """
    Fetch all articles, save new or updated ones as Markdown files, and return IDs of affected articles.

    This function loads existing metadata, fetches all articles, saves only new or updated
    articles, reports the number of new and updated articles, and returns their IDs as an object.

    Returns:
        tuple: (categorized_articles, tracked_metadata) where categorized_articles is a dict with
               'new_articles' (set of new article IDs) and 'updated_articles' (set of updated article IDs),
               and tracked_metadata is the updated metadata dictionary.
    """
    start_time = datetime.now()
    logger.info(f"[Scraper] Starting scraping process at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Ensure articles directory exists
        articles_dir = "articles"
        os.makedirs(articles_dir, exist_ok=True)

        # Load tracked metadata
        tracked_metadata = load_tracked_metadata()

        # Fetch articles
        logger.info("[Scraper] Fetching articles from API...")
        articles = fetch_articles(per_page=10)
        logger.info(f"[Scraper] Retrieved {len(articles)} articles from API")

        # Process articles
        new_count = 0
        updated_count = 0
        skipped_count = 0
        categorized_articles = {"new_articles": set(), "updated_articles": set()}

        logger.info("[Scraper] Processing articles...")
        for article in articles:
            saved, status, article_id = save_article_as_markdown(article, tracked_metadata)
            if saved:
                if status == 'new':
                    new_count += 1
                    categorized_articles["new_articles"].add(article_id)
                elif status == 'updated':
                    updated_count += 1
                    categorized_articles["updated_articles"].add(article_id)
            else:
                skipped_count += 1

        # Save updated tracked metadata
        save_tracked_metadata(tracked_metadata)
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = end_time - start_time
        
        # Log summary
        logger.info(f"[Scraper] Processing completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"[Scraper] Execution time: {execution_time.total_seconds():.2f} seconds")
        logger.info(f"[Scraper] Summary: {len(articles)} total articles processed")
        logger.info(f"[Scraper] Results: {new_count} new, {updated_count} updated, {skipped_count} skipped")
        
        if new_count > 0 or updated_count > 0:
            logger.info(f"[Scraper] Successfully processed {new_count + updated_count} articles")
        else:
            logger.info("[Scraper] No new or updated articles found")

        return categorized_articles, tracked_metadata

    except Exception as e:
        end_time = datetime.now()
        execution_time = end_time - start_time
        logger.error(f"[Scraper] Process failed after {execution_time.total_seconds():.2f} seconds: {e}")
        return {"new_articles": set(), "updated_articles": set()}, {}