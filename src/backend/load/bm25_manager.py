import logging
import os
import pickle

import bm25s

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
BM25_INDEX_PATH = os.path.join(PROJECT_ROOT, "workmate_db", "bm25_index.pkl")


class BM25Manager:
    def __init__(self):
        self.index = None
        self.chunks: list[str] = []
        self.metadatas: list[dict] = []
        self.ids: list[str] = []

    def build_index(self, chunks: list[str], metadatas: list[dict], ids: list[str]):
        self.chunks = chunks
        self.metadatas = metadatas
        self.ids = ids

        corpus_indices = list(range(len(chunks)))
        indexed_texts = [
            f"{m.get('title', '')} {c}".lower()
            for c, m in zip(chunks, metadatas)
        ]
        tokenized_corpus = bm25s.tokenize(indexed_texts)
        self.index = bm25s.BM25(corpus=corpus_indices)
        self.index.index(tokenized_corpus)
        logger.info(f"BM25 index built with {len(chunks)} documents")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        if self.index is None:
            logger.warning("BM25 index not built, returning empty results")
            return []

        k = min(top_k, len(self.chunks))
        query_tokens = bm25s.tokenize([query.lower()])
        results, _ = self.index.retrieve(query_tokens, k=k)

        output = []
        for idx in results[0]:
            meta = self.metadatas[idx]
            output.append({
                "chunk_id": self.ids[idx],
                "text": self.chunks[idx],
                "page_title": meta.get("title", "Unknown Source"),
                "section": meta.get("parent_title", ""),
                **meta,
            })
        return output

    def save(self, path: str = BM25_INDEX_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "index": self.index,
                    "chunks": self.chunks,
                    "metadatas": self.metadatas,
                    "ids": self.ids,
                },
                f,
            )
        logger.info(f"BM25 index saved to {path}")

    def load(self, path: str = BM25_INDEX_PATH):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.index = data["index"]
        self.chunks = data["chunks"]
        self.metadatas = data["metadatas"]
        self.ids = data["ids"]
        logger.info(f"BM25 index loaded from {path} ({len(self.chunks)} documents)")
