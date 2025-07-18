from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as md
from ..config import setup_logging

# Configure logging for the scraper module
logger = setup_logging()

def clean_html(html):
    """
    Clean HTML by removing unwanted elements while preserving content structure.

    Args:
        html (str): The HTML content to clean.

    Returns:
        str: The cleaned HTML as a string.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove unwanted elements (simplified approach)
        unwanted_selectors = [
            'nav', 'aside', 'footer', 'header',
            '.nav', '.navigation', '.ads', '.advertisement',
            '.breadcrumb', '.sidebar', '.social', '.share',
            'script', 'style', 'noscript'
        ]

        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()

        # Remove empty paragraphs and divs
        for tag in soup.find_all(['p', 'div']):
            if not tag.get_text().strip():
                tag.decompose()

        return str(soup)

    except Exception as e:
        logger.error(f"[Converter] HTML cleaning failed: {e}")
        return html  # Return original HTML if cleaning fails

def convert_article_to_markdown(article):
    """
    Convert an article dictionary to a Markdown string.

    This function takes an article dictionary, cleans its HTML body, converts it to Markdown,
    and formats it with the article's title and a link to the original article.

    Args:
        article (dict): The article dictionary containing 'title', 'body', and 'html_url'.

    Returns:
        str: The formatted Markdown content.
    """
    try:
        title = article.get('title', 'No Title')
        body = article.get('body', '')
        html_url = article.get('html_url', '')
        article_id = article.get('id', 'unknown')

        logger.debug(f"[Converter] Converting article ID {article_id}: '{title}'")

        # Step 1: Clean the HTML directly, no need decode
        cleaned_html = clean_html(body)

        # Step 2: Convert to Markdown with preserved elements
        markdown_content = md(
            cleaned_html,
            heading_style='ATX',
            bullets='-',
            convert=['a', 'b', 'strong', 'i', 'em', 'code', 'pre',
                     'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                     'p', 'br', 'ul', 'ol', 'li', 'blockquote']
        )

        # Clean up the markdown formatting
        markdown_content = markdown_content.strip()

        # Format the final markdown with title and source link
        markdown = f"# {title}\n\n"
        markdown += f"[View Original Article]({html_url})\n\n"
        markdown += markdown_content

        logger.info(f"[Converter] Successfully converted article ID {article_id}: '{title}'")
        return markdown
    
    except Exception as e:
        article_id = article.get('id', 'unknown')
        title = article.get('title', 'No Title')
        logger.error(f"[Converter] Failed to convert article {article_id} ('{title}'): {e}")
        return f"# {title}\n\nConversion failed: {str(e)}"