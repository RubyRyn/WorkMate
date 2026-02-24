import os
import google.generativeai as genai
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from dotenv import load_dotenv

load_dotenv()


class GoogleEmbedder(EmbeddingFunction):
    """
    Custom embedding function using Google's text-embedding-004 model.
    Implements ChromaDB's EmbeddingFunction protocol.
    """

    def __init__(self, model_name="models/text-embedding-004"):
        self.model_name = model_name

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(
                "⚠️ WARNING: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment."
            )

        genai.configure(api_key=api_key)

    def __call__(self, input: Documents) -> Embeddings:
        """
        Embeds a list of documents using the Google Generative AI API.
        """
        if not input:
            return []

        embeddings = []
        # The API technically supports batch embedding, but testing document by document
        # to ensure resilience and avoid potential limits for simple implementation
        for doc in input:
            if not doc.strip():
                # Chroma requires an embedding even for empty strings in some cases,
                # though we filter them out earlier. Provide a zero vector if needed,
                # but better to let the API handle or skip.
                continue

            try:
                result = genai.embed_content(
                    model=self.model_name,
                    content=doc,
                    task_type="retrieval_document",
                )
                embeddings.append(result["embedding"])
            except Exception as e:
                print(f"❌ Error embedding document: {e}")
                # Append a dummy embedding or handle error appropriately. Re-raising here.
                raise e

        return embeddings
