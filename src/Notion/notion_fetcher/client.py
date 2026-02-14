"""
Notion API client with rate limiting and pagination support.
"""

import requests
import time
from typing import Generator, Optional


class NotionClient:
    """
    Low-level client for Notion API.
    Handles authentication, rate limiting, and pagination.
    """
    
    BASE_URL = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"
    
    # Rate limit: 3 requests per second for free tier
    REQUEST_DELAY = 0.35  # seconds between requests
    
    def __init__(self, auth_token: str):
        """
        Initialize the Notion client.
        
        Args:
            auth_token: Notion integration token (starts with 'secret_')
        """
        self.auth_token = auth_token
        self._last_request_time = 0
        
        self._headers = {
            "Authorization": f"Bearer {auth_token}",
            "Notion-Version": self.API_VERSION,
            "Content-Type": "application/json",
        }
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Make an API request with rate limiting.
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response as dict
            
        Raises:
            requests.HTTPError: On API errors
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self._headers, **kwargs)
        
        if response.status_code == 429:
            # Rate limited - wait and retry
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return self._request(method, endpoint, **kwargs)
        
        response.raise_for_status()
        return response.json()
    
    def search(
        self, 
        query: str = "", 
        filter_type: Optional[str] = None
    ) -> Generator[dict, None, None]:
        """
        Search the workspace for pages and databases.
        
        Args:
            query: Search query (empty for all)
            filter_type: "page" or "database" to filter results
            
        Yields:
            Search result objects
        """
        payload = {}
        
        if query:
            payload["query"] = query
        
        if filter_type:
            payload["filter"] = {"property": "object", "value": filter_type}
        
        yield from self._paginate("/search", payload)
    
    def get_page(self, page_id: str) -> dict:
        """
        Get a page by ID.
        
        Args:
            page_id: The page ID
            
        Returns:
            Page object
        """
        return self._request("GET", f"/pages/{page_id}")
    
    def get_block_children(self, block_id: str) -> Generator[dict, None, None]:
        """
        Get children blocks of a block or page.
        
        Args:
            block_id: The block or page ID
            
        Yields:
            Block objects
        """
        yield from self._paginate(f"/blocks/{block_id}/children", method="GET")
    
    def get_database(self, database_id: str) -> dict:
        """
        Get a database by ID.
        
        Args:
            database_id: The database ID
            
        Returns:
            Database object
        """
        return self._request("GET", f"/databases/{database_id}")
    
    def query_database(
        self, 
        database_id: str, 
        filter_obj: Optional[dict] = None,
        sorts: Optional[list] = None
    ) -> Generator[dict, None, None]:
        """
        Query a database for rows.
        
        Args:
            database_id: The database ID
            filter_obj: Optional filter object
            sorts: Optional sort configuration
            
        Yields:
            Page objects (database rows)
        """
        payload = {}
        
        if filter_obj:
            payload["filter"] = filter_obj
        
        if sorts:
            payload["sorts"] = sorts
        
        yield from self._paginate(f"/databases/{database_id}/query", payload)
    
    def _paginate(
        self, 
        endpoint: str, 
        payload: Optional[dict] = None,
        method: str = "POST"
    ) -> Generator[dict, None, None]:
        """
        Handle pagination for list endpoints.
        
        Args:
            endpoint: API endpoint
            payload: Request payload (for POST)
            method: HTTP method
            
        Yields:
            Result objects
        """
        payload = payload or {}
        has_more = True
        next_cursor = None
        
        while has_more:
            if next_cursor:
                payload["start_cursor"] = next_cursor
            
            if method == "POST":
                response = self._request(method, endpoint, json=payload)
            else:
                response = self._request(method, endpoint, params=payload)
            
            results = response.get("results", [])
            for item in results:
                yield item
            
            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")
