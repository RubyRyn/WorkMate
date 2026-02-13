"""
Fetch a single Notion page by its ID.
"""

from notion_fetcher.client import NotionClient
from notion_fetcher.fetchers.page_fetcher import PageFetcher


def fetch_page_by_id(token: str, page_id: str):
    """
    Fetch a single page from Notion by its ID.
    
    Args:
        token: Notion integration token
        page_id: The page ID (from URL or API)
    
    Returns:
        NotionDocument object
    """
    # Initialize client and fetcher
    client = NotionClient(token)
    page_fetcher = PageFetcher(client)
    
    # Fetch the page
    document = page_fetcher.fetch_page(page_id)
    
    return document


def main():
    # ===== CONFIGURE THESE =====
    NOTION_TOKEN = "###"
    PAGE_ID = "###"  
    
    # ===========================
    
    # How to find your page ID:
    # 1. Open the page in Notion
    # 2. Look at the URL: https://notion.so/Your-Page-Title-abc123def456
    # 3. The page ID is the last part: abc123def456
    # 4. Or use the full UUID format: abc123de-f456-7890-abcd-ef1234567890
    
    print(f"Fetching page: {PAGE_ID}")
    print("-" * 50)
    
    document = fetch_page_by_id(NOTION_TOKEN, PAGE_ID)

    print(document)

    print("-" * 50)
    
    if document:
        print(f"Title: {document.title}")
        print(f"URL: {document.url}")
        print(f"Source Type: {document.source_type}")
        print(f"Created: {document.created_time}")
        print(f"Last Edited: {document.last_edited_time}")
        print("-" * 50)
        print("Content:")
        print(document.content)
        print("-" * 50)
        print("\nFull text (for embedding):")
        print(document.get_full_text())
    else:
        print("Page not found or has no content.")


if __name__ == "__main__":
    main()