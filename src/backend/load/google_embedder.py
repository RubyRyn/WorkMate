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
    """

    def __init__(self, model_name="gemini-embedding-001"):
        self.model_name = model_name

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(
                "⚠️ WARNING: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment."
            )

        self.client = genai.Client(api_key=api_key)

    def name(self) -> str:
        return "google_embedder"

    def __call__(self, input: Documents) -> Embeddings:
        """
        Embeds a list of documents using the Google Generative AI API.
        Retries on rate limit errors.
        """
        if not input:
            return []

        embeddings = []
        for doc in input:
            if not doc.strip():
                continue

            for attempt in range(3):
                try:
                    result = self.client.models.embed_content(
                        model=self.model_name,
                        contents=doc,
                    )
                    embeddings.append(result.embeddings[0].values)
                    break
                except genai_errors.ClientError as e:
                    if "429" in str(e) and attempt < 2:
                        wait = 45 * (attempt + 1)
                        print(f"⏳ Rate limited. Waiting {wait}s...")
                        time.sleep(wait)
                    else:
                        raise e

        return embeddings
