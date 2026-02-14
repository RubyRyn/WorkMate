"""
Main entry point for Notion data fetching.
"""

import json
import os
from typing import List
import os

from Notion_Fetcher import NotionFetcher


def main():
    """Example usage."""
    # Get token from environment variable
    token = os.environ.get("NOTION_TOKEN")
    
    if not token:
        print("Error: NOTION_TOKEN environment variable not set")
        print("Usage: export NOTION_TOKEN='secret_your_token_here'")
        return
    
    # Initialize fetcher
    fetcher = NotionFetcher(token)
    
    # Fetch all content
    documents = fetcher.fetch_all()
    
    # Print summary
    print("\n=== Summary ===")
    pages = [d for d in documents if d.source_type == "page"]
    rows = [d for d in documents if d.source_type == "database_row"]
    print(f"Pages: {len(pages)}")
    print(f"Database rows: {len(rows)}")
    
    # Save to file
    fetcher.save_to_json(documents, "notion_data.json")
    
    # Print first document as example
    if documents:
        print("\n=== Example Document ===")
        print(documents[0])
        print("\nFull text for embedding:")
        print(documents[0].get_full_text()[:500])


if __name__ == "__main__":
    main()
