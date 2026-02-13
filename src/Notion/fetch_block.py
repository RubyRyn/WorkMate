"""
Fetch a Notion block and its children by block ID.
"""

from notion_fetcher.client import NotionClient
from notion_fetcher.parsers.block_parser import BlockParser


def fetch_block_by_id(token: str, block_id: str, max_depth: int = 5):
    """
    Fetch a block and all its children from Notion.
    
    Args:
        token: Notion integration token
        block_id: The block ID
        max_depth: Maximum depth for nested blocks
    
    Returns:
        Tuple of (block_info, content_text, all_blocks)
    """
    client = NotionClient(token)
    parser = BlockParser()
    
    # Get the block itself
    block_info = get_block_info(client, block_id)
    
    # Fetch all children recursively
    all_blocks = []
    content_text = fetch_children_recursive(
        client, 
        parser, 
        block_id, 
        all_blocks,
        depth=0, 
        max_depth=max_depth
    )
    
    return block_info, content_text, all_blocks


def get_block_info(client: NotionClient, block_id: str) -> dict:
    """Get information about the block itself."""
    return client._request("GET", f"/blocks/{block_id}")


def fetch_children_recursive(
    client: NotionClient,
    parser: BlockParser,
    block_id: str,
    all_blocks: list,
    depth: int = 0,
    max_depth: int = 5
) -> str:
    """
    Recursively fetch block children and extract text.
    
    Args:
        client: NotionClient instance
        parser: BlockParser instance
        block_id: Parent block ID
        all_blocks: List to collect all blocks
        depth: Current recursion depth
        max_depth: Maximum recursion depth
    
    Returns:
        Combined text content
    """
    if depth >= max_depth:
        return ""
    
    texts = []
    indent = "  " * depth
    
    for block in client.get_block_children(block_id):
        all_blocks.append(block)
        
        # Parse this block's text
        text = parser.parse_block(block)
        if text:
            texts.append(f"{indent}{text}")
        
        # Recursively fetch children
        if block.get("has_children", False):
            child_text = fetch_children_recursive(
                client,
                parser,
                block["id"],
                all_blocks,
                depth + 1,
                max_depth
            )
            if child_text:
                texts.append(child_text)
    
    return "\n".join(texts)


def main():
    # ===== CONFIGURE THESE =====
    NOTION_TOKEN = "###"
    BLOCK_ID = "###"
    MAX_DEPTH = 10  # How deep to fetch nested blocks
    # ===========================
    
    print(f"Fetching block: {BLOCK_ID}")
    print("-" * 50)
    
    block_info, content_text, all_blocks = fetch_block_by_id(
        NOTION_TOKEN,
        BLOCK_ID,
        max_depth=MAX_DEPTH
    )
    
    # Print block info
    print("Block Info:")
    print(f"  ID: {block_info.get('id')}")
    print(f"  Type: {block_info.get('type')}")
    print(f"  Has Children: {block_info.get('has_children')}")
    print(f"  Created: {block_info.get('created_time')}")
    print(f"  Last Edited: {block_info.get('last_edited_time')}")
    
    # Print parent info
    parent = block_info.get("parent", {})
    parent_type = parent.get("type")
    print(f"  Parent Type: {parent_type}")
    if parent_type == "page_id":
        print(f"  Parent Page ID: {parent.get('page_id')}")
    elif parent_type == "database_id":
        print(f"  Parent Database ID: {parent.get('database_id')}")
    elif parent_type == "block_id":
        print(f"  Parent Block ID: {parent.get('block_id')}")
    
    print("-" * 50)
    print(f"Total child blocks found: {len(all_blocks)}")
    print("-" * 50)
    
    print("Sample of first 3 child blocks:")
    for i, block in enumerate(all_blocks[:3]):
        print(f"  {i+1}. {block.get('type', 'unknown')} - ID: {block.get('id')}")

    
    # Print block types summary
    if all_blocks:
        print("Block types:")
        type_counts = {}
        for block in all_blocks:
            block_type = block.get("type", "unknown")
            type_counts[block_type] = type_counts.get(block_type, 0) + 1
        for block_type, count in sorted(type_counts.items()):
            print(f"  {block_type}: {count}")
    
    print("-" * 50)
    print("Content:")
    print(content_text if content_text else "(No text content)")
    
    # Save to file
    print("-" * 50)
    output_file = "block_content.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Block ID: {BLOCK_ID}\n")
        f.write(f"Block Type: {block_info.get('type')}\n")
        f.write(f"Total Children: {len(all_blocks)}\n")
        f.write("-" * 50 + "\n")
        f.write(content_text)
    print(f"Content saved to: {output_file}")


if __name__ == "__main__":
    main()