import logging

from src.backend.load.bm25_manager import BM25Manager
from src.backend.load.chroma_manager import ChromaManager

logger = logging.getLogger(__name__)


class HybridRetriever:
    def __init__(self, chroma_manager: ChromaManager, bm25_manager: BM25Manager):
        self.chroma = chroma_manager
        self.bm25 = bm25_manager

    def search(
        self,
        query: str,
        vector_top_k: int = 15,
        bm25_top_k: int = 15,
        final_top_k: int = 15,
        where: dict | None = None,
    ) -> list[dict]:
        vector_results = self._query_chroma(query, vector_top_k, where=where)
        bm25_results = self.bm25.search(query, top_k=bm25_top_k, where=where)

        merged = self.reciprocal_rank_fusion([vector_results, bm25_results])
        return merged[:final_top_k]

    def _query_chroma(self, query: str, top_k: int, where: dict | None = None) -> list[dict]:
        results = self.chroma.query(query, n_results=top_k, where=where)
        output = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results.get("metadatas", [[]])[0]
            ids = results.get("ids", [[]])[0]
            for doc, meta, chunk_id in zip(docs, metas, ids):
                output.append({
                    "chunk_id": chunk_id,
                    "text": doc.strip().replace("\r\n", "\n"),
                    "page_title": meta.get("title", "Unknown Source"),
                    "section": meta.get("section_header") or meta.get("parent_title", ""),
                    **meta,
                })
        return output

    def reciprocal_rank_fusion(
        self, results_lists: list[list[dict]], k: int = 60
    ) -> list[dict]:
        scores: dict[str, float] = {}
        chunk_data: dict[str, dict] = {}

        for results in results_lists:
            for rank, chunk in enumerate(results):
                chunk_id = chunk["chunk_id"]
                scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (k + rank + 1)
                if chunk_id not in chunk_data:
                    chunk_data[chunk_id] = chunk

        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        return [chunk_data[cid] for cid in sorted_ids]
