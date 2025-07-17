from bs4 import BeautifulSoup
from markdownify import markdownify as md

def clean_html(html):
    """
    Clean HTML by removing unwanted elements.

    This function removes navigation, ads, aside, footer, and breadcrumb elements from the HTML.

    Args:
        html (str): The HTML content to clean.

    Returns:
        str: The cleaned HTML as a string.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.select('nav, aside, footer, .nav, .ads, .advertisement, .breadcrumb'):
            tag.decompose()
        return str(soup)
    except Exception as e:
        print(f"Failed to clean HTML: {e}")
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
        cleaned_html = clean_html(body)
        markdown_content = md(cleaned_html, strip=['a'])
        markdown_content = markdown_content.strip()
        markdown = f"# {title}\n\n"
        markdown += f"[View Original Article]({html_url})\n\n"
        markdown += markdown_content
        return markdown
    except Exception as e:
        print(f"Failed to convert article to Markdown: {e}")
        return ""  # Return empty string if conversion fails