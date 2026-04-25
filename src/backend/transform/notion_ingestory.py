import json
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.backend.load.chroma_manager import ChromaManager
from src.backend.load.bm25_manager import BM25Manager, BM25_INDEX_PATH

class NotionIngestor:
    def __init__(self, file_path="./notion_data.json", chunk_size=1000, chunk_overlap=200, workspace_id=None):
        """
        Initializes the ingestion pipeline, database connection, and splitters.
        """
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.workspace_id = workspace_id

        # Instantiate the database manager
        self.db = ChromaManager()

        # Setup splitters on initialization
        self._setup_splitters()

    def _setup_splitters(self):
        """Private method to configure the LangChain splitters."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            # Custom separators tailored for technical documentation in order of preference
            separators=["\n\n", "\n```\n", "\n---", "\n- ", "\n", " ", ""],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )

    def _load_data(self):
        """Private method to load the raw JSON data."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _deduplicate_docs(self, raw_docs):
        """
        Remove duplicate documents by ID.
        Notion's search API returns database rows as both pages and database rows,
        so the same document can appear twice. Prefer the 'database_row' version
        since it contains richer property metadata.
        """
        seen = {}
        for doc in raw_docs:
            doc_id = doc.get("id")
            if doc_id in seen:
                # Keep the database_row version over the page version
                if doc.get("source_type") == "database_row":
                    seen[doc_id] = doc
            else:
                seen[doc_id] = doc
        return list(seen.values())

    def _build_parent_child_maps(self, raw_docs):
        """
        Build lookup maps for parent-child relationships.

        Returns:
            id_to_doc: dict mapping document ID to document
            parent_to_children: dict mapping parent ID to list of child documents
        """
        id_to_doc = {}
        parent_to_children = {}

        for doc in raw_docs:
            doc_id = doc.get("id")
            parent_id = doc.get("parent_id")
            id_to_doc[doc_id] = doc

            if parent_id:
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = []
                parent_to_children[parent_id].append(doc)

        return id_to_doc, parent_to_children

    def _enrich_content(self, doc, id_to_doc, parent_to_children):
        """
        Enrich a document's content with parent context and database properties.
        Child pages are indexed separately, so their summaries are not appended here
        to avoid content cross-contamination.
        """
        content = doc.get("content", "")
        parent_id = doc.get("parent_id")

        enriched_parts = []

        # If this doc has a parent in our data, prepend parent context
        if parent_id and parent_id in id_to_doc:
            parent_doc = id_to_doc[parent_id]
            parent_title = parent_doc.get("title", "Untitled")
            enriched_parts.append(f"[Parent Page: {parent_title}]\n")

        # For database rows, prepend structured properties so they're searchable
        if doc.get("source_type") == "database_row" and doc.get("properties"):
            prop_lines = []
            for key, value in doc["properties"].items():
                if key.startswith("_"):
                    continue
                if key.lower() in ("title", "name"):
                    continue
                if value is None or value == "" or value == []:
                    continue
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                prop_lines.append(f"{key}: {value}")
            if prop_lines:
                enriched_parts.append("[Properties]\n" + "\n".join(prop_lines) + "\n")

        enriched_parts.append(content)

        return "\n".join(enriched_parts)

    def _extract_section_header(self, chunk_text, previous_header):
        """
        Find heading markers (produced by BlockParser) in a chunk's text.
        Returns (section_header_for_this_chunk, heading_to_carry_forward).
        """
        headings = re.findall(r'^(#{1,3})\s+(.+)$', chunk_text, re.MULTILINE)
        if headings:
            last_heading = headings[-1][1].strip()
            first_heading = headings[0][1].strip()
            # If the chunk starts with a heading, use it as the section
            first_line = chunk_text.lstrip().split('\n')[0]
            if re.match(r'^#{1,3}\s+', first_line):
                return first_heading, last_heading
            else:
                return previous_header, last_heading
        return previous_header, previous_header

    def chunk_documents(self, raw_docs):
        """
        Reusable method to convert raw Notion documents into chunks, metadatas, and ids.
        Does NOT interact with the database.
        """
        raw_docs = self._deduplicate_docs(raw_docs)
        id_to_doc, parent_to_children = self._build_parent_child_maps(raw_docs)

        all_chunks = []
        all_metadatas = []
        all_ids = []

        for doc in raw_docs:
            chunks, metadatas, ids = self._process_document(doc, id_to_doc, parent_to_children)
            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
            all_ids.extend(ids)

        return all_chunks, all_metadatas, all_ids

    def _process_document(self, doc, id_to_doc, parent_to_children):
        """
        Chunk a single document using RecursiveCharacterTextSplitter.
        """
        content = self._enrich_content(doc, id_to_doc, parent_to_children)
        if not content.strip():
            return [], [], []

        physical_splits = self.text_splitter.create_documents([content])

        chunks = []
        metadatas = []
        ids = []

        parent_id = doc.get("parent_id")
        parent_title = None
        if parent_id and parent_id in id_to_doc:
            parent_title = id_to_doc[parent_id].get("title", "Untitled")

        current_section = ""
        for i, chunk in enumerate(physical_splits):
            chunks.append(chunk.page_content)

            section_header, current_section = self._extract_section_header(
                chunk.page_content, current_section
            )

            chunk_metadata = {
                "parent_id": doc.get("id"),
                "title": doc.get("title", "Untitled"),
                "url": doc.get("url"),
                "source_type": doc.get("source_type", "page"),
                "chunk_index": i,
                "section_header": section_header,
            }

            if self.workspace_id:
                chunk_metadata["workspace_id"] = self.workspace_id

            if parent_title:
                chunk_metadata["parent_title"] = parent_title
            if parent_id:
                chunk_metadata["notion_parent_id"] = parent_id
            if doc.get("created_time"):
                chunk_metadata["created_time"] = doc["created_time"]
            if doc.get("last_edited_time"):
                chunk_metadata["last_edited_time"] = doc["last_edited_time"]

            metadatas.append(chunk_metadata)
            ids.append(f"{doc['id']}_{i}")

        return chunks, metadatas, ids

    def run_pipeline(self):
        """Public method to execute the full ingestion pipeline."""
        print(f"Loading data from {self.file_path}...")
        raw_docs = self._load_data()
        all_chunks, all_metadatas, all_ids = self.chunk_documents(raw_docs)

        if all_chunks:
            print(f"Storing {len(all_chunks)} chunks into Chroma...")
            self.db.add_documents(all_chunks, all_metadatas, all_ids)

            print("Building BM25 index...")
            bm25 = BM25Manager()
            bm25.build_index(all_chunks, all_metadatas, all_ids)
            bm25.save(BM25_INDEX_PATH)
            print(f"BM25 index saved to {BM25_INDEX_PATH}")
        else:
            print("No chunks were created.")

    def run_pipeline_from_docs(self, raw_docs):
        """Run the ingestion pipeline from in-memory document dicts (no file I/O)."""
        all_chunks, all_metadatas, all_ids = self.chunk_documents(raw_docs)

        if all_chunks:
            print(f"Storing {len(all_chunks)} chunks into Chroma...")
            self.db.add_documents(all_chunks, all_metadatas, all_ids)

            print("Building BM25 index...")
            bm25 = BM25Manager()
            bm25.build_index(all_chunks, all_metadatas, all_ids)
            bm25.save(BM25_INDEX_PATH)
            print(f"BM25 index saved to {BM25_INDEX_PATH}")
        else:
            print("No chunks were created.")

# --- Execution ---
if __name__ == "__main__":
    # The instantiation is clean, and the parameters can easily be swapped for testing.
    ingestor = NotionIngestor(file_path="../../data/notion_data.json")
    ingestor.db.reset()
    ingestor.run_pipeline()

    # The teammate changed this test query, using their query instead.
    result = ingestor.db.query("What is the purpose of this document?", n_results=10)
    print("Query Results:", result["documents"][:1])
