"""
Fetcher for Notion pages and their block content.
"""

from typing import List, Optional
from datetime import datetime

from notion_fetcher.client import NotionClient
from notion_fetcher.parsers.block_parser import BlockParser
from notion_fetcher.models.document import NotionDocument


class PageFetcher:
    """
    Fetches Notion pages and extracts their content.
    Handles nested blocks recursively.
    """

    def __init__(self, client: NotionClient):
        """
        Initialize the page fetcher.

        Args:
            client: NotionClient instance
        """
        self.client = client
        self.parser = BlockParser()

    def fetch_all_pages(self) -> List[NotionDocument]:
        """
        Fetch all pages in the workspace.

        Returns:
            List of NotionDocument objects
        """
        documents = []

        print("Searching for pages...")
        for page in self.client.search(filter_type="page"):
            try:
                doc = self.fetch_page(page["id"], page_data=page)
                if doc:
                    documents.append(doc)
                    print(f"  Fetched: {doc.title}")
            except Exception as e:
                print(f"  Error fetching page {page['id']}: {e}")

        print(f"Total pages fetched: {len(documents)}")
        return documents

    def fetch_page(
        self, page_id: str, page_data: Optional[dict] = None
    ) -> Optional[NotionDocument]:
        """
        Fetch a single page and its content.

        Args:
            page_id: The page ID
            page_data: Optional pre-fetched page data

        Returns:
            NotionDocument or None if page has no content
        """
        # Get page metadata if not provided
        if not page_data:
            page_data = self.client.get_page(page_id)

        # Extract title
        title = self._extract_title(page_data)

        # Get page URL
        url = page_data.get("url")

        # Extract timestamps
        created_time = self._parse_timestamp(page_data.get("created_time"))
        last_edited_time = self._parse_timestamp(page_data.get("last_edited_time"))

        # Get parent info
        parent_id = self._extract_parent_id(page_data)

        # Fetch all blocks (content)
        content = self._fetch_blocks_recursive(page_id)

        # Skip pages with no content
        if not content.strip():
            return None

        return NotionDocument(
            id=page_id,
            title=title,
            content=content,
            source_type="page",
            url=url,
            parent_id=parent_id,
            created_time=created_time,
            last_edited_time=last_edited_time,
        )

    def _fetch_blocks_recursive(
        self, block_id: str, depth: int = 0, max_depth: int = 5
    ) -> str:
        """
        Recursively fetch blocks and their children.

        Args:
            block_id: The block or page ID
            depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            Combined text content
        """
        if depth >= max_depth:
            return ""

        texts = []

        for block in self.client.get_block_children(block_id):
            # Parse this block
            text = self.parser.parse_block(block)
            if text:
                # Add indentation for nested blocks
                indent = "  " * depth
                texts.append(f"{indent}{text}")

            # Recursively fetch children if they exist
            if block.get("has_children", False):
                child_content = self._fetch_blocks_recursive(
                    block["id"], depth + 1, max_depth
                )
                if child_content:
                    texts.append(child_content)

        return "\n".join(texts)

    def _extract_title(self, page_data: dict) -> str:
        """Extract title from page properties."""
        properties = page_data.get("properties", {})

        # Find the property of type "title" (name varies in databases)
        for _, prop in properties.items():
            if isinstance(prop, dict) and prop.get("type") == "title":
                title_array = prop.get("title", [])
                if title_array and isinstance(title_array, list):
                    # Join all text parts of the title
                    title_text = "".join(
                        t.get("plain_text", "")
                        for t in title_array
                        if isinstance(t, dict)
                    )
                    if title_text:
                        return title_text

        return "Untitled"

    def _extract_parent_id(self, page_data: dict) -> Optional[str]:
        """Extract parent ID from page data."""
        parent = page_data.get("parent", {})
        parent_type = parent.get("type")

        if parent_type == "page_id":
            return parent.get("page_id")
        elif parent_type == "database_id":
            return parent.get("database_id")
        elif parent_type == "workspace":
            return None

        return None

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO timestamp string to datetime."""
        if not timestamp_str:
            return None

        try:
            # Handle Notion's timestamp format
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            return None
