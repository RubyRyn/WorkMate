import logging
import os

import chromadb
from dotenv import load_dotenv
from google import genai

from src.backend.load.google_embedder import GoogleEmbedder

load_dotenv()

logger = logging.getLogger(__name__)

# Resolve the project root (3 levels up from src/backend/load/chroma_manager.py)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "workmate_db")


class ChromaManager:
    def __init__(self, db_path=DEFAULT_DB_PATH, collection_name="notion_docs"):
        """
        Initialize the ChromaDB client and collection.
        :param db_path: Path to the persistent database directory.
        :param collection_name: Name of the collection to use.
        """
        self.db_path = db_path
        self.collection_name = collection_name

        # Initialize Google Embedder (gemini-embedding-001)
        self.embedder = GoogleEmbedder()

        # Initialize Client
        chroma_host = os.getenv("CHROMA_HOST")
        chroma_port = os.getenv("CHROMA_PORT", "8000")

        if chroma_host:
            logger.info(f"Connecting to ChromaDB at {chroma_host}:{chroma_port} via HttpClient")
            self.client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        else:
            logger.info(f"Connecting to ChromaDB at {db_path} via PersistentClient")
            self.client = chromadb.PersistentClient(path=db_path)

        # Open collection WITHOUT embedding_function to avoid ChromaDB's
        # conflict detection. We embed manually in add_documents() and query().
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
        print(
            f"Connected to ChromaDB at '{db_path}' (Collection: '{collection_name}') with Google Embedder"
        )

    def add_documents(self, documents, metadatas, ids, batch_size=20):
        """
        Add documents to the collection in batches.
        Embeds using Google Embedder before storing.
        """
        total = len(documents)
        for i in range(0, total, batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            try:
                # Generate embeddings with Google Embedder
                embeddings = self.embedder(batch_docs)
                self.collection.upsert(
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids,
                    embeddings=embeddings,
                )
                print(f"Added batch {i // batch_size + 1} ({len(batch_docs)} docs, {i + len(batch_docs)}/{total})")
            except Exception as e:
                print(f"Error adding batch {i // batch_size + 1}: {e}")
                raise e

    def query(self, query_text, n_results=5, where=None):
        """
        Search the collection for relevant documents.
        Embeds the query using Google Embedder before searching.
        """
        print(f"Querying: '{query_text}'...")

        # Embed the query with the same Google model used during ingestion
        query_embedding = self.embedder([query_text])

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return results

    def get_by_parent(self, parent_id, limit=20):
        """
        Fetch all chunks belonging to a parent document.
        Used for sibling chunk expansion at retrieval time.
        """
        results = self.collection.get(
            where={"parent_id": parent_id},
            limit=limit,
            include=["documents", "metadatas"],
        )
        return results

    def delete_by_workspace(self, workspace_id: str):
        """Delete all chunks belonging to a specific workspace."""
        try:
            self.collection.delete(where={"workspace_id": workspace_id})
            print(f"Deleted all chunks for workspace '{workspace_id}'")
        except Exception as e:
            logger.error(f"Error deleting chunks for workspace {workspace_id}: {e}")
            raise

    def reset(self):
        """
        DANGER: Deletes and recreates the collection.
        Useful for testing/dev environments.
        """
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            self.collection_name
        )
        print(f"Collection '{self.collection_name}' has been reset.")
