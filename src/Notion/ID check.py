"""
Debug script to check what a Notion ID points to.
Helps identify if an ID is a page, database, or invalid.
"""

import requests


def check_notion_id(token: str, object_id: str):
    """
    Check what type of object a Notion ID refers to.
    
    Args:
        token: Notion integration token
        object_id: The ID to check
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    
    base_url = "https://api.notion.com/v1"
    
    print(f"Checking ID: {object_id}")
    print("-" * 50)
    
    # Try as a page
    print("Trying as PAGE...")
    response = requests.get(f"{base_url}/pages/{object_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ SUCCESS! This is a PAGE")
        print(f"  Object type: {data.get('object')}")
        print(f"  URL: {data.get('url')}")
        
        # Check if it's a database page (row)
        parent = data.get("parent", {})
        if parent.get("type") == "database_id":
            print(f"  Note: This page is a ROW in database: {parent.get('database_id')}")
        return
    else:
        print(f"  ✗ Not a page (Error: {response.status_code})")
        if response.status_code == 404:
            print("    → ID not found or not shared with integration")
        elif response.status_code == 400:
            print("    → Invalid ID format")
    
    # Try as a database
    print("\nTrying as DATABASE...")
    response = requests.get(f"{base_url}/databases/{object_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        title = "".join(item.get("plain_text", "") for item in data.get("title", []))
        print(f"  ✓ SUCCESS! This is a DATABASE")
        print(f"  Title: {title or 'Untitled'}")
        print(f"  URL: {data.get('url')}")
        return
    else:
        print(f"  ✗ Not a database (Error: {response.status_code})")
        if response.status_code == 404:
            print("    → ID not found or not shared with integration")
        elif response.status_code == 400:
            print("    → Invalid ID format")
    
    # Try as a block
    print("\nTrying as BLOCK...")
    response = requests.get(f"{base_url}/blocks/{object_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ SUCCESS! This is a BLOCK")
        print(f"  Block type: {data.get('type')}")
        return
    else:
        print(f"  ✗ Not a block (Error: {response.status_code})")
    
    print("\n" + "=" * 50)
    print("CONCLUSION: Could not identify this ID.")
    print("Possible reasons:")
    print("  1. The integration is not connected to this page/database")
    print("  2. The ID is incorrect")
    print("  3. The page/database was deleted")
    print("\nTo fix: Open the page in Notion → ••• menu → Add connections → Select your integration")


def main():
    # ===== CONFIGURE THESE =====
    NOTION_TOKEN = "###"
    OBJECT_ID = "###"
    # ===========================
    
    check_notion_id(NOTION_TOKEN, OBJECT_ID)


if __name__ == "__main__":
    main()