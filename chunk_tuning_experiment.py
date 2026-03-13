"""
chunk_tuning_experiment.py
─────────────────────────
Automated grid-search experiment for tuning chunk_size and chunk_overlap
in the WorkMate RAG pipeline.

For each configuration it:
  1. Chunks the Notion data
  2. Computes chunk statistics (count, min/max/avg/median length)
  3. Ingests into a temporary ChromaDB collection
  4. Runs a fixed set of test queries → records top-3 retrieved chunks
  5. Saves all results to chunk_tuning_results.json

Usage:
    uv run python chunk_tuning_experiment.py
"""

from __future__ import annotations

import json
import os
import shutil
import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# ─── Constants ────────────────────────────────────────────────────────
DATA_PATH = Path("src/data/notion_data.json")
TEMP_DB_DIR = Path("chroma_db_experiment")  # isolated from production
COLLECTION = "experiment"
RESULTS_FILE = Path("chunk_tuning_results.json")

# ─── Test Queries ─────────────────────────────────────────────────────
TEST_QUERIES = [
    {
        "id": "q1",
        "question": "Who is responsible for deployment?",
        "type": "factoid",
    },
    {
        "id": "q2",
        "question": "What is the purpose of WorkMate?",
        "type": "broad/definitional",
    },
    {
        "id": "q3",
        "question": "What happened during the last incident?",
        "type": "factoid/event",
    },
    {
        "id": "q4",
        "question": "What are the sprint tasks for the backend team?",
        "type": "list",
    },
    {
        "id": "q5",
        "question": "How does the CI/CD pipeline work?",
        "type": "analytical",
    },
    {
        "id": "q6",
        "question": "What are the main features of the project?",
        "type": "broad",
    },
]

# ─── Experiment Grid ──────────────────────────────────────────────────
CONFIGS = [
    {"label": "A_baseline", "chunk_size": 1000, "chunk_overlap": 200},
    {"label": "B_500_100",  "chunk_size": 500,  "chunk_overlap": 100},
    {"label": "C_500_50",   "chunk_size": 500,  "chunk_overlap": 50},
    {"label": "D_300_60",   "chunk_size": 300,  "chunk_overlap": 60},
    {"label": "E_300_30",   "chunk_size": 300,  "chunk_overlap": 30},
    {"label": "F_750_150",  "chunk_size": 750,  "chunk_overlap": 150},
    {"label": "G_750_75",   "chunk_size": 750,  "chunk_overlap": 75},
]


# ─── Data classes for structured results ──────────────────────────────
@dataclass
class ChunkStats:
    total_chunks: int = 0
    min_length: int = 0
    max_length: int = 0
    avg_length: float = 0.0
    median_length: float = 0.0


@dataclass
class QueryResult:
    query_id: str = ""
    question: str = ""
    query_type: str = ""
    retrieved_chunks: list = field(default_factory=list)


@dataclass
class ExperimentResult:
    label: str = ""
    chunk_size: int = 0
    chunk_overlap: int = 0
    overlap_pct: str = ""
    chunk_stats: ChunkStats = field(default_factory=ChunkStats)
    query_results: list = field(default_factory=list)
    elapsed_seconds: float = 0.0


# ─── Chunking logic (mirrors NotionIngestor) ─────────────────────────
HEADERS_TO_SPLIT = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

SEPARATORS = ["\n\n", "\n```\n", "\n---", "\n- ", "\n", " ", ""]


def chunk_documents(raw_docs: list[dict], chunk_size: int, chunk_overlap: int):
    """Return (texts, metadatas, ids) for a given config."""
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT)
    text_splitter = RecursiveCharacterTextSplitter(
        separators=SEPARATORS,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    all_texts, all_metas, all_ids = [], [], []
    for doc in raw_docs:
        content = doc.get("content", "")
        if not content:
            continue

        md_splits = md_splitter.split_text(content)
        physical_splits = text_splitter.split_documents(md_splits)

        for i, chunk in enumerate(physical_splits):
            all_texts.append(chunk.page_content)
            meta = {
                "parent_id": doc.get("id"),
                "title": doc.get("title", "Untitled"),
                "url": doc.get("url"),
                "source_type": doc.get("source_type", "page"),
                "chunk_index": i,
            }
            meta.update(chunk.metadata)
            all_metas.append(meta)
            all_ids.append(f"{doc['id']}_{i}")

    return all_texts, all_metas, all_ids


def compute_stats(texts: list[str]) -> ChunkStats:
    lengths = [len(t) for t in texts]
    if not lengths:
        return ChunkStats()
    return ChunkStats(
        total_chunks=len(lengths),
        min_length=min(lengths),
        max_length=max(lengths),
        avg_length=round(statistics.mean(lengths), 1),
        median_length=round(statistics.median(lengths), 1),
    )


# ─── Custom embedder using the NEW google.genai SDK ──────────────────
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from dotenv import load_dotenv
from google import genai

load_dotenv()

EMBED_MODEL = "gemini-embedding-001"


class NewGoogleEmbedder(EmbeddingFunction):
    """Embedder using the current google.genai SDK and gemini-embedding-001.
    Includes rate-limit handling: pauses between batches of 80 to stay under
    the free-tier limit of 100 embed requests/minute.
    """

    BATCH_SIZE = 80   # embeddings per batch (free tier = 100 req/min)
    PAUSE_SECS = 45   # seconds to wait between batches

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set")
        self.client = genai.Client(api_key=api_key)
        self._call_count = 0  # track calls within a minute window

    def __call__(self, input: Documents) -> Embeddings:
        if not input:
            return []
        embeddings = []
        for idx, doc in enumerate(input):
            if not doc.strip():
                continue

            # Rate-limit: pause after every BATCH_SIZE calls
            if self._call_count > 0 and self._call_count % self.BATCH_SIZE == 0:
                print(f"    ⏳ Rate limit: pausing {self.PAUSE_SECS}s after {self._call_count} embeddings...")
                time.sleep(self.PAUSE_SECS)

            result = self.client.models.embed_content(
                model=EMBED_MODEL, contents=doc
            )
            embeddings.append(result.embeddings[0].values)
            self._call_count += 1

        return embeddings


# ─── Experiment runner ────────────────────────────────────────────────
def run_experiment(config: dict, raw_docs: list[dict]) -> ExperimentResult:
    """Run a single experiment for one (chunk_size, chunk_overlap) config."""
    label = config["label"]
    c_size = config["chunk_size"]
    c_overlap = config["chunk_overlap"]
    overlap_pct = f"{round(c_overlap / c_size * 100)}%"

    print(f"\n{'='*60}")
    print(f"  Config: {label}  (size={c_size}, overlap={c_overlap}, {overlap_pct})")
    print(f"{'='*60}")

    t0 = time.time()

    # 1. Chunk
    texts, metas, ids = chunk_documents(raw_docs, c_size, c_overlap)
    stats = compute_stats(texts)
    print(f"  → {stats.total_chunks} chunks  "
          f"(len: {stats.min_length}–{stats.max_length}, "
          f"avg={stats.avg_length}, med={stats.median_length})")

    if not texts:
        print("  ⚠️  No chunks produced, skipping.")
        return ExperimentResult(label=label, chunk_size=c_size,
                                chunk_overlap=c_overlap, overlap_pct=overlap_pct)

    # 2. Ingest into temp collection (batch to respect rate limits)
    db_path = str(TEMP_DB_DIR / label)
    if Path(db_path).exists():
        shutil.rmtree(db_path)

    client = chromadb.PersistentClient(path=db_path)
    embedder = NewGoogleEmbedder()
    collection = client.get_or_create_collection(
        name=COLLECTION, embedding_function=embedder
    )

    # Add documents in batches to let the embedder pace its API calls
    BATCH = 80
    for batch_start in range(0, len(texts), BATCH):
        batch_end = min(batch_start + BATCH, len(texts))
        collection.add(
            documents=texts[batch_start:batch_end],
            metadatas=metas[batch_start:batch_end],
            ids=ids[batch_start:batch_end],
        )
        print(f"  → Ingested batch {batch_start}–{batch_end} of {len(texts)}")
    print(f"  → All {len(texts)} chunks ingested into {db_path}")

    # 3. Run test queries
    query_results = []
    for q in TEST_QUERIES:
        results = collection.query(query_texts=[q["question"]], n_results=3)

        retrieved = []
        if results["documents"] and results["documents"][0]:
            for j, doc_text in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][j] if results.get("metadatas") else {}
                distance = (
                    results["distances"][0][j] if results.get("distances") else None
                )
                retrieved.append({
                    "rank": j + 1,
                    "title": meta.get("title", "?"),
                    "chunk_index": meta.get("chunk_index", "?"),
                    "distance": round(distance, 4) if distance else None,
                    "text_preview": doc_text[:200] + ("..." if len(doc_text) > 200 else ""),
                })

        qr = QueryResult(
            query_id=q["id"],
            question=q["question"],
            query_type=q["type"],
            retrieved_chunks=retrieved,
        )
        query_results.append(qr)
        print(f"  → {q['id']}: retrieved {len(retrieved)} chunks")

    elapsed = round(time.time() - t0, 2)

    return ExperimentResult(
        label=label,
        chunk_size=c_size,
        chunk_overlap=c_overlap,
        overlap_pct=overlap_pct,
        chunk_stats=stats,
        query_results=query_results,
        elapsed_seconds=elapsed,
    )


# ─── Stats-only mode (no API calls) ──────────────────────────────────
STATS_FILE = Path("chunk_tuning_stats.json")


def run_stats_only(raw_docs: list[dict]):
    """Run chunk analysis for all configs without calling embedding APIs."""
    all_results = []

    for config in CONFIGS:
        label = config["label"]
        c_size = config["chunk_size"]
        c_overlap = config["chunk_overlap"]
        overlap_pct = f"{round(c_overlap / c_size * 100)}%"

        texts, metas, ids = chunk_documents(raw_docs, c_size, c_overlap)
        stats = compute_stats(texts)

        # Collect sample chunks (first 3) for inspection
        sample_chunks = []
        for i, (text, meta) in enumerate(zip(texts[:3], metas[:3])):
            sample_chunks.append({
                "index": i,
                "title": meta.get("title", "?"),
                "length": len(text),
                "text_preview": text[:300] + ("..." if len(text) > 300 else ""),
            })

        result = {
            "label": label,
            "chunk_size": c_size,
            "chunk_overlap": c_overlap,
            "overlap_pct": overlap_pct,
            "chunk_stats": asdict(stats),
            "sample_chunks": sample_chunks,
        }
        all_results.append(result)

    # Save
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # Print summary table
    print(f"\n{'─'*80}")
    print(f"{'Config':<16} {'Size':>5} {'Overlap':>7} {'%':>5} {'Chunks':>7} "
          f"{'Min':>5} {'Max':>5} {'Avg':>7} {'Med':>7}")
    print(f"{'─'*80}")
    for r in all_results:
        s = r["chunk_stats"]
        print(f"{r['label']:<16} {r['chunk_size']:>5} {r['chunk_overlap']:>7} "
              f"{r['overlap_pct']:>5} {s['total_chunks']:>7} "
              f"{s['min_length']:>5} {s['max_length']:>5} "
              f"{s['avg_length']:>7} {s['median_length']:>7}")

    print(f"\n✅ Stats saved to {STATS_FILE}")
    return all_results


# ─── Main ─────────────────────────────────────────────────────────────
def main():
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "--stats-only"

    print("📂 Loading Notion data...")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_docs = json.load(f)
    print(f"   Loaded {len(raw_docs)} documents.\n")

    if mode == "--stats-only":
        print("📊 Running in STATS-ONLY mode (no API calls)\n")
        run_stats_only(raw_docs)
        return

    # Full retrieval mode
    print("🔬 Running FULL retrieval experiment (requires embedding API)\n")
    all_results = []

    for config in CONFIGS:
        try:
            result = run_experiment(config, raw_docs)
            all_results.append(asdict(result))

            # Incremental save after each config
            with open(RESULTS_FILE, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, default=str)
            print(f"  💾 Saved progress ({len(all_results)} configs)")

        except Exception as e:
            print(f"  ❌ Config {config['label']} failed: {e}")
            print("     Saving partial results and stopping.")
            break

    print(f"\n✅ Experiment complete. {len(all_results)} configs saved to {RESULTS_FILE}")

    # Print summary table
    print(f"\n{'─'*80}")
    print(f"{'Config':<16} {'Size':>5} {'Overlap':>7} {'%':>5} {'Chunks':>7} "
          f"{'Min':>5} {'Max':>5} {'Avg':>7} {'Med':>7} {'Time':>6}")
    print(f"{'─'*80}")
    for r in all_results:
        s = r["chunk_stats"]
        print(f"{r['label']:<16} {r['chunk_size']:>5} {r['chunk_overlap']:>7} "
              f"{r['overlap_pct']:>5} {s['total_chunks']:>7} "
              f"{s['min_length']:>5} {s['max_length']:>5} "
              f"{s['avg_length']:>7} {s['median_length']:>7} "
              f"{r['elapsed_seconds']:>5}s")

    # Cleanup temp DB
    if TEMP_DB_DIR.exists():
        shutil.rmtree(TEMP_DB_DIR)
        print(f"\n🧹 Cleaned up temp DB at {TEMP_DB_DIR}")


if __name__ == "__main__":
    main()
