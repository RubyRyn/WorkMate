"""
Fetcher for Notion databases and their rows.
"""

from typing import List, Optional, Any
from datetime import datetime

from notion_fetcher.client import NotionClient
from notion_fetcher.parsers.block_parser import BlockParser
from notion_fetcher.models.document import NotionDocument


class DatabaseFetcher:
    """
    Fetches Notion databases and extracts row content.
    Handles various property types.
    """
    
    def __init__(self, client: NotionClient):
        """
        Initialize the database fetcher.
        
        Args:
            client: NotionClient instance
        """
        self.client = client
        self.parser = BlockParser()
    
    def fetch_all_databases(self, include_row_content: bool = True) -> List[NotionDocument]:
        """
        Fetch all databases and their rows.
        
        Args:
            include_row_content: Whether to fetch block content from each row
            
        Returns:
            List of NotionDocument objects (one per row)
        """
        documents = []
        
        print("Searching for databases...")
        for database in self.client.search(filter_type="database"):
            try:
                db_id = database["id"]
                db_title = self._extract_database_title(database)
                print(f"  Found database: {db_title}")
                
                # Fetch all rows from this database
                row_docs = self.fetch_database_rows(
                    db_id, 
                    database_title=db_title,
                    include_content=include_row_content
                )
                documents.extend(row_docs)
                
            except Exception as e:
                print(f"  Error fetching database {database['id']}: {e}")
        
        print(f"Total database rows fetched: {len(documents)}")
        return documents
    
    def fetch_database_rows(
        self, 
        database_id: str,
        database_title: Optional[str] = None,
        include_content: bool = True
    ) -> List[NotionDocument]:
        """
        Fetch all rows from a specific database.
        
        Args:
            database_id: The database ID
            database_title: Optional database title for context
            include_content: Whether to fetch block content from each row
            
        Returns:
            List of NotionDocument objects
        """
        documents = []
        
        for row in self.client.query_database(database_id):
            try:
                doc = self._row_to_document(
                    row, 
                    database_id=database_id,
                    database_title=database_title,
                    include_content=include_content
                )
                if doc:
                    documents.append(doc)
                    print(f"    Row: {doc.title}")
            except Exception as e:
                print(f"    Error processing row {row['id']}: {e}")
        
        return documents
    
    def _row_to_document(
        self, 
        row: dict,
        database_id: str,
        database_title: Optional[str] = None,
        include_content: bool = True
    ) -> Optional[NotionDocument]:
        """
        Convert a database row to a NotionDocument.
        
        Args:
            row: Row data from API
            database_id: Parent database ID
            database_title: Parent database title
            include_content: Whether to fetch block content
            
        Returns:
            NotionDocument or None
        """
        row_id = row["id"]
        
        # Extract all properties
        properties = self._extract_properties(row.get("properties", {}))
        
        # Get title from properties
        title = properties.get("title") or properties.get("Name") or "Untitled Row"
        
        # Get URL
        url = row.get("url")
        
        # Extract timestamps
        created_time = self._parse_timestamp(row.get("created_time"))
        last_edited_time = self._parse_timestamp(row.get("last_edited_time"))
        
        # Fetch block content if requested
        content = ""
        if include_content:
            content = self._fetch_row_content(row_id)
        
        # Add database context to properties
        if database_title:
            properties["_database"] = database_title
        
        # Build content from properties if no block content
        if not content:
            content = self._properties_to_text(properties)
        
        return NotionDocument(
            id=row_id,
            title=title if isinstance(title, str) else str(title),
            content=content,
            source_type="database_row",
            url=url,
            parent_id=database_id,
            properties=properties,
            created_time=created_time,
            last_edited_time=last_edited_time,
        )
    
    def _fetch_row_content(self, row_id: str) -> str:
        """Fetch block content from a database row."""
        texts = []
        
        for block in self.client.get_block_children(row_id):
            text = self.parser.parse_block(block)
            if text:
                texts.append(text)
        
        return "\n".join(texts)
    
    def _extract_properties(self, properties: dict) -> dict:
        """
        Extract values from all properties.
        
        Args:
            properties: Raw properties object from API
            
        Returns:
            Dictionary of property names to values
        """
        extracted = {}
        
        for prop_name, prop_data in properties.items():
            value = self._extract_property_value(prop_data)
            if value is not None:
                extracted[prop_name] = value
        
        return extracted
    
    def _extract_property_value(self, prop_data: dict) -> Optional[Any]:
        """
        Extract value from a single property.
        
        Args:
            prop_data: Property data object
            
        Returns:
            Extracted value or None
        """
        prop_type = prop_data.get("type")
        
        if not prop_type:
            return None
        
        # Handle different property types
        extractors = {
            "title": self._extract_title_property,
            "rich_text": self._extract_rich_text_property,
            "number": lambda p: p.get("number"),
            "select": self._extract_select_property,
            "multi_select": self._extract_multi_select_property,
            "status": self._extract_status_property,
            "date": self._extract_date_property,
            "checkbox": lambda p: p.get("checkbox"),
            "url": lambda p: p.get("url"),
            "email": lambda p: p.get("email"),
            "phone_number": lambda p: p.get("phone_number"),
            "people": self._extract_people_property,
            "relation": self._extract_relation_property,
            "formula": self._extract_formula_property,
            "rollup": self._extract_rollup_property,
            "created_time": lambda p: p.get("created_time"),
            "last_edited_time": lambda p: p.get("last_edited_time"),
            "created_by": self._extract_user_property,
            "last_edited_by": self._extract_user_property,
        }
        
        extractor = extractors.get(prop_type)
        if extractor:
            return extractor(prop_data)
        
        return None
    
    def _extract_title_property(self, prop_data: dict) -> Optional[str]:
        """Extract title property value."""
        title_array = prop_data.get("title", [])
        if title_array:
            return "".join(item.get("plain_text", "") for item in title_array)
        return None
    
    def _extract_rich_text_property(self, prop_data: dict) -> Optional[str]:
        """Extract rich text property value."""
        rich_text = prop_data.get("rich_text", [])
        if rich_text:
            return "".join(item.get("plain_text", "") for item in rich_text)
        return None
    
    def _extract_select_property(self, prop_data: dict) -> Optional[str]:
        """Extract select property value."""
        select = prop_data.get("select")
        if select:
            return select.get("name")
        return None
    
    def _extract_multi_select_property(self, prop_data: dict) -> Optional[List[str]]:
        """Extract multi-select property values."""
        multi_select = prop_data.get("multi_select", [])
        if multi_select:
            return [item.get("name") for item in multi_select if item.get("name")]
        return None
    
    def _extract_status_property(self, prop_data: dict) -> Optional[str]:
        """Extract status property value."""
        status = prop_data.get("status")
        if status:
            return status.get("name")
        return None
    
    def _extract_date_property(self, prop_data: dict) -> Optional[str]:
        """Extract date property value."""
        date = prop_data.get("date")
        if date:
            start = date.get("start", "")
            end = date.get("end", "")
            if end:
                return f"{start} to {end}"
            return start
        return None
    
    def _extract_people_property(self, prop_data: dict) -> Optional[List[str]]:
        """Extract people property values."""
        people = prop_data.get("people", [])
        if people:
            return [person.get("name", "Unknown") for person in people]
        return None
    
    def _extract_relation_property(self, prop_data: dict) -> Optional[List[str]]:
        """Extract relation property values (just IDs)."""
        relations = prop_data.get("relation", [])
        if relations:
            return [rel.get("id") for rel in relations if rel.get("id")]
        return None
    
    def _extract_formula_property(self, prop_data: dict) -> Optional[Any]:
        """Extract formula property value."""
        formula = prop_data.get("formula", {})
        formula_type = formula.get("type")
        if formula_type:
            return formula.get(formula_type)
        return None
    
    def _extract_rollup_property(self, prop_data: dict) -> Optional[Any]:
        """Extract rollup property value."""
        rollup = prop_data.get("rollup", {})
        rollup_type = rollup.get("type")
        if rollup_type:
            return rollup.get(rollup_type)
        return None
    
    def _extract_user_property(self, prop_data: dict) -> Optional[str]:
        """Extract user property value."""
        for key in ["created_by", "last_edited_by"]:
            if key in prop_data:
                user = prop_data[key]
                return user.get("name", "Unknown")
        return None
    
    def _extract_database_title(self, database: dict) -> str:
        """Extract title from database object."""
        title_array = database.get("title", [])
        if title_array:
            return "".join(item.get("plain_text", "") for item in title_array)
        return "Untitled Database"
    
    def _properties_to_text(self, properties: dict) -> str:
        """Convert properties dict to readable text."""
        lines = []
        for key, value in properties.items():
            if key.startswith("_"):
                continue
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO timestamp string to datetime."""
        if not timestamp_str:
            return None
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            return None
