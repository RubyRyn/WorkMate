"""
Custom embedding function using Google's gemini-embedding-001 model.
Implements ChromaDB's EmbeddingFunction protocol.
"""

import os
import time

from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

load_dotenv()


class GoogleEmbedder(EmbeddingFunction):
    """
    Custom embedding function using Google's gemini-embedding-001 model.
    Implements ChromaDB's EmbeddingFunction protocol.
    Includes rate limit handling with automatic retries.
    """

    def __init__(self, model_name="gemini-embedding-001"):
        self.model_name = model_name

        api_key = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ WARNING: No Gemini API key found in environment (GEMINI_KEY / GEMINI_API_KEY).")

        self.client = genai.Client(api_key=api_key)

    def name(self) -> str:
        return "google_embedder"

    def __call__(self, input: Documents) -> Embeddings:
        """Embed a list of documents with automatic rate limit handling."""
        if not input:
            return []

        embeddings = []
        for i, doc in enumerate(input):
            if not doc.strip():
                continue

            for attempt in range(3):
                try:
                    result = self.client.models.embed_content(
                        model=self.model_name,
                        contents=doc,
                    )
                    embeddings.append(result.embeddings[0].values)

                    # Small delay to stay under rate limit (100 req/min = 1 per 0.6s)
                    if i < len(input) - 1:
                        time.sleep(0.7)
                    break

                except genai_errors.ClientError as e:
                    error_str = str(e)
                    if "429" in error_str and attempt < 2:
                        wait_time = 45 * (attempt + 1)
                        print(f"⏳ Rate limited on chunk {i+1}/{len(input)}, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise e

        return embeddings
