"""
Parser for extracting text content from Notion blocks.
"""

from typing import List, Optional


class BlockParser:
    """
    Extracts plain text from Notion block objects.
    Handles various block types and nested content.
    """
    
    # Block types that contain rich_text
    RICH_TEXT_BLOCKS = {
        "paragraph",
        "heading_1",
        "heading_2", 
        "heading_3",
        "bulleted_list_item",
        "numbered_list_item",
        "quote",
        "callout",
        "toggle",
    }
    
    def __init__(self):
        self._parsers = {
            "paragraph": self._parse_rich_text_block,
            "heading_1": self._parse_heading,
            "heading_2": self._parse_heading,
            "heading_3": self._parse_heading,
            "bulleted_list_item": self._parse_rich_text_block,
            "numbered_list_item": self._parse_rich_text_block,
            "quote": self._parse_rich_text_block,
            "callout": self._parse_callout,
            "toggle": self._parse_rich_text_block,
            "to_do": self._parse_todo,
            "code": self._parse_code,
            "table_row": self._parse_table_row,
            "child_page": self._parse_child_page,
            "child_database": self._parse_child_database,
        }
    
    def parse_block(self, block: dict) -> Optional[str]:
        """
        Parse a single block and return its text content.
        
        Args:
            block: Raw block object from Notion API
            
        Returns:
            Extracted text or None if block has no text
        """
        block_type = block.get("type")
        
        if not block_type:
            return None
        
        parser = self._parsers.get(block_type)
        
        if parser:
            return parser(block)
        
        # For unsupported block types, try generic rich_text extraction
        if block_type in self.RICH_TEXT_BLOCKS:
            return self._parse_rich_text_block(block)
        
        return None
    
    def parse_blocks(self, blocks: List[dict]) -> str:
        """
        Parse multiple blocks and combine into a single text.
        
        Args:
            blocks: List of block objects
            
        Returns:
            Combined text content
        """
        texts = []
        
        for block in blocks:
            text = self.parse_block(block)
            if text:
                texts.append(text)
        
        return "\n".join(texts)
    
    def _extract_rich_text(self, rich_text_array: List[dict]) -> str:
        """Extract plain text from a rich_text array."""
        if not rich_text_array:
            return ""
        
        parts = []
        for item in rich_text_array:
            plain_text = item.get("plain_text", "")
            if plain_text:
                parts.append(plain_text)
        
        return "".join(parts)
    
    def _parse_rich_text_block(self, block: dict) -> Optional[str]:
        """Parse blocks that have a standard rich_text structure."""
        block_type = block.get("type")
        block_data = block.get(block_type, {})
        rich_text = block_data.get("rich_text", [])
        
        return self._extract_rich_text(rich_text) or None
    
    def _parse_heading(self, block: dict) -> Optional[str]:
        """Parse heading blocks with level indicator."""
        block_type = block.get("type")
        block_data = block.get(block_type, {})
        rich_text = block_data.get("rich_text", [])
        
        text = self._extract_rich_text(rich_text)
        if not text:
            return None
        
        # Add heading marker for context
        level = block_type[-1]  # "heading_1" -> "1"
        return f"{'#' * int(level)} {text}"
    
    def _parse_callout(self, block: dict) -> Optional[str]:
        """Parse callout blocks (includes icon + text)."""
        block_data = block.get("callout", {})
        rich_text = block_data.get("rich_text", [])
        
        text = self._extract_rich_text(rich_text)
        if not text:
            return None
        
        return f"[Callout] {text}"
    
    def _parse_todo(self, block: dict) -> Optional[str]:
        """Parse to-do blocks with checkbox state."""
        block_data = block.get("to_do", {})
        rich_text = block_data.get("rich_text", [])
        checked = block_data.get("checked", False)
        
        text = self._extract_rich_text(rich_text)
        if not text:
            return None
        
        checkbox = "[x]" if checked else "[ ]"
        return f"{checkbox} {text}"
    
    def _parse_code(self, block: dict) -> Optional[str]:
        """Parse code blocks with language."""
        block_data = block.get("code", {})
        rich_text = block_data.get("rich_text", [])
        language = block_data.get("language", "")
        
        text = self._extract_rich_text(rich_text)
        if not text:
            return None
        
        return f"[Code: {language}]\n{text}"
    
    def _parse_table_row(self, block: dict) -> Optional[str]:
        """Parse table row blocks."""
        block_data = block.get("table_row", {})
        cells = block_data.get("cells", [])
        
        cell_texts = []
        for cell in cells:
            cell_text = self._extract_rich_text(cell)
            cell_texts.append(cell_text or "")
        
        if not any(cell_texts):
            return None
        
        return " | ".join(cell_texts)
    
    def _parse_child_page(self, block: dict) -> Optional[str]:
        """Parse child page reference."""
        block_data = block.get("child_page", {})
        title = block_data.get("title", "Untitled")
        
        return f"[Child Page: {title}]"
    
    def _parse_child_database(self, block: dict) -> Optional[str]:
        """Parse child database reference."""
        block_data = block.get("child_database", {})
        title = block_data.get("title", "Untitled")
        
        return f"[Child Database: {title}]"
