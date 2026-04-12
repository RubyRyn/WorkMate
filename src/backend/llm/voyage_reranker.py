from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

DEFAULT_RERANK_MODEL = "rerank-2"
RELEVANCE_THRESHOLD = 0.4


class VoyageReranker:
    """
    Reranks retrieved chunks using the VoyageAI rerank API.
    Replaces the LLM-based filter_chunks step in the RAG pipeline.
    """

    def __init__(
        self,
        model: str = DEFAULT_RERANK_MODEL,
        threshold: float = RELEVANCE_THRESHOLD,
    ):
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            logger.warning(
                "[VoyageReranker] VOYAGE_API_KEY not set — reranking disabled. "
                "Set VOYAGE_API_KEY in .env to enable VoyageAI reranking."
            )
            self.client = None
        else:
            import voyageai
            self.client = voyageai.Client(api_key=api_key)

        self.model = model
        self.threshold = threshold

    def rerank(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
        top_k: int = 5,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Rerank chunks by relevance to the query.

        Returns:
            final_chunks  — top_k chunks above threshold, score field stripped (clean for generation)
            scored_chunks — all input chunks sorted by score descending, with rerank_score added
        """
        if not chunks:
            return [], []

        if self.client is None:
            logger.warning("[VoyageReranker] Reranking skipped (no API key). Returning top_k unranked.")
            return chunks[:top_k], []

        documents = [
            f"Page: {c['page_title']}\nSection: {c['section']}\n{c['text']}"
            if c.get("section")
            else f"Page: {c['page_title']}\n{c['text']}"
            for c in chunks
        ]

        try:
            result = self.client.rerank(
                query=query,
                documents=documents,
                model=self.model,
                top_k=len(chunks),  # fetch all scores; we apply threshold + top_k ourselves
            )

            scored_chunks: List[Dict[str, Any]] = []
            for item in result.results:
                chunk = chunks[item.index]
                scored_chunks.append({**chunk, "rerank_score": round(item.relevance_score, 4)})

            scored_chunks.sort(key=lambda x: x["rerank_score"], reverse=True)

            logger.info(
                f"[VoyageReranker] scores: "
                f"{[(c['page_title'], c['rerank_score']) for c in scored_chunks]}"
            )

            above_threshold = [c for c in scored_chunks if c["rerank_score"] >= self.threshold]
            final_scored = above_threshold[:top_k]

            if not final_scored:
                logger.warning(
                    f"[VoyageReranker] All {len(chunks)} chunks below threshold "
                    f"({self.threshold}). Top score: "
                    f"{scored_chunks[0]['rerank_score'] if scored_chunks else 'N/A'}."
                )

            # Strip rerank_score before passing to generation prompt
            final_chunks = [
                {k: v for k, v in c.items() if k != "rerank_score"} for c in final_scored
            ]

            return final_chunks, scored_chunks

        except Exception as e:
            logger.warning(
                f"[VoyageReranker] Reranking failed, falling back to top {top_k} unranked: {e}"
            )
            return chunks[:top_k], []
