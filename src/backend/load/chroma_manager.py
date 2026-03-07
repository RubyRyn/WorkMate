import logging
import os

import chromadb
from dotenv import load_dotenv
from google import genai

from src.backend.load.google_embedder import GoogleEmbedder

load_dotenv()

logger = logging.getLogger(__name__)


class ChromaManager:
    def __init__(self, db_path="chroma_db", collection_name="notion_docs"):
        """
        Initialize the ChromaDB client and collection.
        :param db_path: Path to the persistent database directory.
        :param collection_name: Name of the collection to use.
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedder = GoogleEmbedder()

        # Initialize Persistent Client
        self.client = chromadb.PersistentClient(path=db_path)

        # Get or Create Collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name, embedding_function=self.embedder
            )
        except ValueError as e:
            if "Embedding function conflict" in str(e):
                print(
                    f"⚠️ Embedding function conflict. Recreating collection '{collection_name}'..."
                )
                self.client.delete_collection(collection_name)
                self.collection = self.client.get_or_create_collection(
                    name=collection_name, embedding_function=self.embedder
                )
            else:
                raise e
        print(
            f"✅ Connected to ChromaDB at '{db_path}' (Collection: '{collection_name}')"
        )

    # Metadata is to also be stored in the postgres database, so we can query it separately if needed.
    def add_documents(self, documents, metadatas, ids, batch_size=20):
        """
        Add documents to the collection in batches.
        :param documents: List of text strings.
        :param metadatas: List of dictionaries containing metadata.
        :param ids: List of unique string IDs.
        :param batch_size: Number of documents per batch.
        """
        total = len(documents)
        for i in range(0, total, batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            try:
                self.collection.add(documents=batch_docs, metadatas=batch_meta, ids=batch_ids)
                print(f"✅ Added batch {i // batch_size + 1} ({len(batch_docs)} docs, {i + len(batch_docs)}/{total})")
            except Exception as e:
                print(f"❌ Error adding batch {i // batch_size + 1}: {e}")
                raise e

    def query(self, query_text, n_results=2, where=None):
        """
        Search the collection for relevant documents.
        Uses ChromaDB's default embedding function (all-MiniLM-L6-v2)
        to match the stored 384-dimension vectors.
        :param query_text: The question or text to search for.
        :param n_results: Number of results to return.
        :param where: (Optional) Metadata filter dictionary.
        :return: A dictionary of results.
        """
        print(f"🔍 Querying: '{query_text}'...")

        results = self.collection.query(
            query_texts=[query_text], n_results=n_results, where=where
        )
        return results

    def reset(self):
        """
        DANGER: Deletes and recreates the collection.
        Useful for testing/dev environments.
        """
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, embedding_function=self.embedder
        )
        print(f"⚠️ Collection '{self.collection_name}' has been reset.")


# --- Usage Example ---
if __name__ == "__main__":
    db = ChromaManager()

    docs = [
        "The authentication system uses OAuth2 with Google.",
        "The database schema was updated to include user roles on 2023-10-12.",
        "API rate limits are set to 100 requests per minute.",
        "The frontend is built using React and Cloudflare Pages.",
    ]
    meta = [
        {"source": "auth_spec.md", "tag": "security"},
        {"source": "db_changelog.md", "tag": "database"},
        {"source": "api_config.md", "tag": "performance"},
        {"source": "architecture.md", "tag": "frontend"},
    ]
    ids = ["doc1", "doc2", "doc3", "doc4"]

    # Check if data already exists to avoid duplicates
    if db.collection.count() == 0:
        db.add_documents(docs, meta, ids)
    else:
        print("ℹ️  Data already exists. Skipping insertion.")

    results = db.query("How do we handle user login?")

    if results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            print(f"Result {i + 1}: {doc}")
            print(f"Metadata: {results['metadatas'][0][i]}")
            print("-" * 20)

    # Search with filters
    print("\n--- Filtered Search (Tag: database) ---")
    filtered_results = db.query("What changed recently?", where={"tag": "database"})
    if filtered_results["documents"]:
        print(filtered_results["documents"][0])

    db.reset()
