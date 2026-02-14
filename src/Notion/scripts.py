import os
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
from notion_fetcher.Notion_Fetcher import NotionFetcher

# Initialize
fetcher = NotionFetcher(NOTION_TOKEN)

# Fetch everything
documents = fetcher.fetch_all()

# Or fetch separately
# pages = fetcher.fetch_pages_only()
# db_rows = fetcher.fetch_databases_only()

# Save to JSON for later use
fetcher.save_to_json(documents, "notion_data.json")

# Each document has:
for doc in documents:
    print(doc.id)           # Notion page/row ID
    print(doc.title)        # Title
    print(doc.content)      # Text content
    print(doc.source_type)  # "page" or "database_row"
    print(doc.url)          # Link back to Notion
    print(doc.get_full_text())  # Ready for embedding