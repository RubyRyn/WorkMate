"""
Data models for Notion content.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class NotionDocument:
    """
    Represents a piece of content extracted from Notion.
    Ready to be chunked and embedded.
    """
    id: str
    title: str
    content: str
    source_type: str  # "page" or "database_row"
    url: Optional[str] = None
    parent_id: Optional[str] = None
    properties: dict = field(default_factory=dict)  # For database row properties
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    
    def __str__(self) -> str:
        preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"NotionDocument(title='{self.title}', type={self.source_type}, preview='{preview}')"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source_type": self.source_type,
            "url": self.url,
            "parent_id": self.parent_id,
            "properties": self.properties,
            "created_time": self.created_time.isoformat() if self.created_time else None,
            "last_edited_time": self.last_edited_time.isoformat() if self.last_edited_time else None,
        }
    
    def get_full_text(self) -> str:
        """
        Get full text representation including title and properties.
        Useful for embedding.
        """
        parts = [f"Title: {self.title}"]
        
        # Add properties if it's a database row
        if self.properties:
            props_text = ", ".join(f"{k}: {v}" for k, v in self.properties.items() if v)
            if props_text:
                parts.append(f"Properties: {props_text}")
        
        if self.content:
            parts.append(f"Content: {self.content}")
        
        return "\n".join(parts)
