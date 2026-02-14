from typing import List
import json
from notion_fetcher.client import NotionClient
from notion_fetcher.fetchers.page_fetcher import PageFetcher
from notion_fetcher.fetchers.database_fetcher import DatabaseFetcher
from notion_fetcher.models.document import NotionDocument




class NotionFetcher:
    """
    Main class that orchestrates fetching all content from Notion.
    """
    
    def __init__(self, auth_token: str):
        """
        Initialize the Notion fetcher.
        
        Args:
            auth_token: Notion integration token
        """
        self.client = NotionClient(auth_token)
        self.page_fetcher = PageFetcher(self.client)
        self.database_fetcher = DatabaseFetcher(self.client)
    
    def fetch_all(self, include_database_content: bool = True) -> List[NotionDocument]:
        """
        Fetch all pages and database rows from the workspace.
        
        Args:
            include_database_content: Whether to fetch block content from database rows
            
        Returns:
            List of all NotionDocument objects
        """
        documents = []
        
        # Fetch pages
        print("\n=== Fetching Pages ===")
        pages = self.page_fetcher.fetch_all_pages()
        documents.extend(pages)
        
        # Fetch databases
        print("\n=== Fetching Databases ===")
        db_rows = self.database_fetcher.fetch_all_databases(
            include_row_content=include_database_content
        )
        documents.extend(db_rows)
        
        print(f"\n=== Total Documents: {len(documents)} ===")
        return documents
    
    def fetch_pages_only(self) -> List[NotionDocument]:
        """Fetch only pages (no databases)."""
        print("\n=== Fetching Pages ===")
        return self.page_fetcher.fetch_all_pages()
    
    def fetch_databases_only(self, include_content: bool = True) -> List[NotionDocument]:
        """Fetch only database rows (no standalone pages)."""
        print("\n=== Fetching Databases ===")
        return self.database_fetcher.fetch_all_databases(
            include_row_content=include_content
        )
    
    def save_to_json(self, documents: List[NotionDocument], filepath: str):
        """
        Save documents to a JSON file.
        
        Args:
            documents: List of NotionDocument objects
            filepath: Output file path
        """
        data = [doc.to_dict() for doc in documents]
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(documents)} documents to {filepath}")

