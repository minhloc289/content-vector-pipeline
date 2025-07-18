import os
from ..config import setup_logging

# Configure logging for the file handlers module
logger = setup_logging()

def get_article_file_path(article_id: str) -> str:
    """
    Get the file path for a given article ID.

    Args:
        article_id (str): The ID of the article.

    Returns:
        str: The file path to the article's Markdown file.
    """
    return os.path.join("articles", article_id, f"{article_id}.md")

def validate_article_file_paths(categorized_articles):
    """
    Validate Markdown file paths for new and updated articles.

    Args:
        categorized_articles (dict): Dict with 'new_articles' and 'updated_articles' sets.

    Returns:
        tuple: (valid_paths, missing_paths) lists of existing and non-existent files.
    """
    logger.debug("[FileHandlers] Starting file path validation")
    
    all_article_ids = categorized_articles["new_articles"] | categorized_articles["updated_articles"]
    
    if not all_article_ids:
        logger.info("[FileHandlers] No articles to validate")
        return [], []

    logger.debug(f"[FileHandlers] Validating {len(all_article_ids)} article file paths")

    # Construct and validate Markdown file paths
    file_paths = [
        get_article_file_path(article_id)
        for article_id in all_article_ids
    ]
    
    valid_paths = []
    missing_paths = []
    
    for path in file_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            missing_paths.append(path)
    
    # Log validation results
    logger.info(f"[FileHandlers] Path validation completed: {len(valid_paths)} valid, {len(missing_paths)} missing")
    
    if missing_paths:
        logger.warning(f"[FileHandlers] Missing files detected: {len(missing_paths)} articles")
        for missing_path in missing_paths:
            logger.debug(f"[FileHandlers] Missing: {missing_path}")
    
    return valid_paths, missing_paths