"""
Detailed debug script to test Notion API access.
"""
import os
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
import requests


def debug_notion_access(token: str, object_id: str):
    """Test all possible API endpoints with detailed error messages."""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    
    base_url = "https://api.notion.com/v1"
    
    # Also try without dashes
    object_id_no_dashes = object_id.replace("-", "")
    
    print(f"Testing ID: {object_id}")
    print(f"Without dashes: {object_id_no_dashes}")
    print("=" * 60)
    
    # Test 1: Get as block
    print("\n1. GET /blocks/{id}")
    print("-" * 40)
    response = requests.get(f"{base_url}/blocks/{object_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Type: {data.get('type')}")
        print(f"   Has Children: {data.get('has_children')}")
        print(f"   Parent: {data.get('parent')}")
    else:
        print(f"   Error: {response.text[:200]}")
    
    # Test 2: Get block children
    print("\n2. GET /blocks/{id}/children")
    print("-" * 40)
    response = requests.get(f"{base_url}/blocks/{object_id}/children", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        results = data.get("results", [])
        print(f"   Children count: {len(results)}")
        if results:
            print(f"   First child type: {results[0].get('type')}")
            print(f"   First child ID: {results[0].get('id')}")
    else:
        print(f"   Error: {response.text[:200]}")
    
    # Test 3: Get as database
    print("\n3. GET /databases/{id}")
    print("-" * 40)
    response = requests.get(f"{base_url}/databases/{object_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        title = data.get("title", [])
        title_text = "".join(t.get("plain_text", "") for t in title)
        print(f"   Title: {title_text}")
        print(f"   Properties: {list(data.get('properties', {}).keys())}")
    else:
        print(f"   Error: {response.text[:200]}")
    
    # Test 4: Query database
    print("\n4. POST /databases/{id}/query")
    print("-" * 40)
    response = requests.post(f"{base_url}/databases/{object_id}/query", headers=headers, json={})
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        results = data.get("results", [])
        print(f"   Rows count: {len(results)}")
        if results:
            print(f"   First row ID: {results[0].get('id')}")
            # Show properties of first row
            props = results[0].get("properties", {})
            print(f"   First row properties: {list(props.keys())}")
    else:
        print(f"   Error: {response.text[:200]}")
    
    # Test 5: Get as page
    print("\n5. GET /pages/{id}")
    print("-" * 40)
    response = requests.get(f"{base_url}/pages/{object_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   URL: {data.get('url')}")
    else:
        print(f"   Error: {response.text[:200]}")
    
    # Test 6: Search for this ID
    print("\n6. POST /search (searching for content)")
    print("-" * 40)
    response = requests.post(f"{base_url}/search", headers=headers, json={"page_size": 10})
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        results = data.get("results", [])
        print(f"   Total items found: {len(results)}")
        for item in results[:5]:
            item_id = item.get("id")
            item_type = item.get("object")
            # Get title
            if item_type == "page":
                props = item.get("properties", {})
                title_prop = props.get("title") or props.get("Title") or props.get("Name") or {}
                title_arr = title_prop.get("title", [])
                title = "".join(t.get("plain_text", "") for t in title_arr) or "Untitled"
            else:
                title_arr = item.get("title", [])
                title = "".join(t.get("plain_text", "") for t in title_arr) or "Untitled"
            
            match = " ← THIS ONE!" if item_id.replace("-", "") == object_id_no_dashes else ""
            print(f"   - [{item_type}] {title} ({item_id[:8]}...){match}")
    else:
        print(f"   Error: {response.text[:200]}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)


def main():
    # ===== CONFIGURE THESE =====
    OBJECT_ID = "###"  
    # ===========================
    
    debug_notion_access(NOTION_TOKEN, OBJECT_ID)


if __name__ == "__main__":
    main()
