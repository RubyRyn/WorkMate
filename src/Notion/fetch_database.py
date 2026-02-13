"""
Fetch a Notion database and its rows by database ID.
"""

from notion_fetcher.client import NotionClient
from notion_fetcher.fetchers.database_fetcher import DatabaseFetcher


def fetch_database_by_id(token: str, database_id: str, include_content: bool = True):
    """
    Fetch a database and all its rows from Notion.
    
    Args:
        token: Notion integration token
        database_id: The database ID (from URL or API)
        include_content: Whether to fetch block content from each row
    
    Returns:
        List of NotionDocument objects (one per row)
    """
    # Initialize client and fetcher
    client = NotionClient(token)
    database_fetcher = DatabaseFetcher(client)
    
    # Get database title first
    db_info = client.get_database(database_id)
    db_title = "".join(
        item.get("plain_text", "") 
        for item in db_info.get("title", [])
    ) or "Untitled Database"
    
    # Fetch all rows
    documents = database_fetcher.fetch_database_rows(
        database_id=database_id,
        database_title=db_title,
        include_content=include_content
    )
    
    return db_title, documents


def main():
    # ===== CONFIGURE THESE =====
    
    NOTION_TOKEN = "###"
    DATABASE_ID = "###"
    INCLUDE_ROW_CONTENT = True  # Set to False for faster fetching (properties only)
    
    
    print(f"Fetching database: {DATABASE_ID}")
    print("-" * 50)
    
    db_title, documents = fetch_database_by_id(
        NOTION_TOKEN, 
        DATABASE_ID,
        include_content=INCLUDE_ROW_CONTENT
    )
    
    print(f"Database: {db_title}")
    print(f"Total rows: {len(documents)}")
    print("-" * 50)
    
    # Print each row
    for i, doc in enumerate(documents, 1):
        print(f"\n--- Row {i}: {doc.title} ---")
        print(f"ID: {doc.id}")
        print(f"URL: {doc.url}")
        
        # Print properties
        if doc.properties:
            print("Properties:")
            for key, value in doc.properties.items():
                if not key.startswith("_"):
                    print(f"  {key}: {value}")
        
        # Print content if available
        if doc.content:
            print("Content:")
            # Show first 200 chars
            preview = doc.content[:200]
            if len(doc.content) > 200:
                preview += "..."
            print(f"  {preview}")
    
    print("\n" + "=" * 50)
    print("Full text for first row (for embedding):")
    if documents:
        print(documents[0].get_full_text())


if __name__ == "__main__":
    main()