"""
Unified Notion fetch + ChromaDB ingestion script.

Usage:
    uv run python ingest.py                  # fetch from Notion + ingest
    uv run python ingest.py --ingest-only    # skip fetch, use existing JSON
    uv run python ingest.py --fetch-only     # fetch only, don't ingest
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "Notion"))

DEFAULT_DATA_PATH = PROJECT_ROOT / "src" / "data" / "notion_data.json"


def fetch(data_path: Path):
    """Fetch all content from Notion and save to JSON."""
    from notion_fetcher.Notion_Fetcher import NotionFetcher

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("ERROR: NOTION_TOKEN not set in environment.")
        sys.exit(1)

    fetcher = NotionFetcher(token)
    documents = fetcher.fetch_all()
    fetcher.save_to_json(documents, str(data_path))
    print(f"\nSaved {len(documents)} documents to {data_path}")


def ingest(data_path: Path):
    """Ingest JSON into ChromaDB + BM25."""
    from src.backend.transform.notion_ingestory import NotionIngestor

    if not data_path.exists():
        print(f"ERROR: Data file not found at {data_path}")
        sys.exit(1)

    ingestor = NotionIngestor(file_path=str(data_path))
    ingestor.db.reset()
    ingestor.run_pipeline()
    print("\nIngestion complete.")


def main():
    parser = argparse.ArgumentParser(description="WorkMate Notion ingestion pipeline")
    parser.add_argument(
        "--fetch-only", action="store_true", help="Fetch from Notion only, skip ingestion"
    )
    parser.add_argument(
        "--ingest-only", action="store_true", help="Ingest existing JSON only, skip fetch"
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"Path to JSON data file (default: {DEFAULT_DATA_PATH})",
    )
    args = parser.parse_args()

    if args.fetch_only and args.ingest_only:
        print("ERROR: Cannot use --fetch-only and --ingest-only together.")
        sys.exit(1)

    if not args.ingest_only:
        fetch(args.data_path)
    if not args.fetch_only:
        ingest(args.data_path)


if __name__ == "__main__":
    main()
