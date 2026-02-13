"""
Fetch a child_database (inline database) from Notion.
This handles databases that are embedded in pages.
"""

from notion_fetcher.client import NotionClient
from notion_fetcher.fetchers.database_fetcher import DatabaseFetcher


def fetch_child_database(token: str, database_id: str, include_content: bool = True):
    """
    Fetch an inline/child database and all its rows.
    
    Args:
        token: Notion integration token
        database_id: The database/block ID
        include_content: Whether to fetch content inside each row
    
    Returns:
        Tuple of (database_info, documents)
    """
    client = NotionClient(token)
    database_fetcher = DatabaseFetcher(client)
    
    # Get database info
    db_info = client.get_database(database_id)
    
    # Extract title
    db_title = "".join(
        item.get("plain_text", "") 
        for item in db_info.get("title", [])
    ) or "Untitled Database"
    
    # Get database properties (columns)
    properties = db_info.get("properties", {})
    
    # Fetch all rows
    documents = database_fetcher.fetch_database_rows(
        database_id=database_id,
        database_title=db_title,
        include_content=include_content
    )
    
    return {
        "id": database_id,
        "title": db_title,
        "properties": properties,
    }, documents


def main():
    # ===== CONFIGURE THESE =====
    NOTION_TOKEN = "###"
    DATABASE_ID = "###"
    INCLUDE_ROW_CONTENT = True
    # ===========================
    
    print(f"Fetching child_database: {DATABASE_ID}")
    print("=" * 60)
    
    try:
        db_info, documents = fetch_child_database(
            NOTION_TOKEN,
            DATABASE_ID,
            include_content=INCLUDE_ROW_CONTENT
        )
        
        # Print database info
        print(f"Database Title: {db_info['title']}")
        print(f"Total Rows: {len(documents)}")
        print("-" * 60)
        
        # Print column names (properties)
        print("Columns (Properties):")
        for prop_name, prop_data in db_info["properties"].items():
            prop_type = prop_data.get("type", "unknown")
            print(f"  - {prop_name} ({prop_type})")
        print("-" * 60)
        
        # Print each row
        for i, doc in enumerate(documents, 1):
            print(f"\n{'='*60}")
            print(f"ROW {i}: {doc.title}")
            print(f"{'='*60}")
            print(f"ID: {doc.id}")
            print(f"URL: {doc.url}")
            
            # Print all properties
            if doc.properties:
                print("\nProperties:")
                for key, value in doc.properties.items():
                    if not key.startswith("_"):  # Skip internal properties
                        # Format lists nicely
                        if isinstance(value, list):
                            value = ", ".join(str(v) for v in value)
                        print(f"  {key}: {value}")
            
            # Print content (text inside the row)
            if doc.content:
                print("\nContent:")
                print("-" * 40)
                print(doc.content)
            else:
                print("\nContent: (empty)")
            
            print()
        
        # Save all data to file
        print("=" * 60)
        output_file = "database_content.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Database: {db_info['title']}\n")
            f.write(f"Total Rows: {len(documents)}\n")
            f.write("=" * 60 + "\n\n")
            
            for i, doc in enumerate(documents, 1):
                f.write(f"ROW {i}: {doc.title}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Full text for embedding:\n")
                f.write(doc.get_full_text())
                f.write("\n\n")
        
        print(f"Content saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the integration is connected to this database")
        print("2. Open the database in Notion → ••• → Add connections → Select your integration")


if __name__ == "__main__":
    main()