import json
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from src.backend.load.chroma_manager import ChromaManager

class NotionIngestor:
    def __init__(self, file_path="./notion_data.json", chunk_size=500, chunk_overlap=100):
        """
        Initializes the ingestion pipeline, database connection, and splitters.
        """
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Instantiate the database manager
        self.db = ChromaManager()
        
        # Setup splitters on initialization
        self._setup_splitters()

    def _setup_splitters(self):
        """Private method to configure the LangChain splitters."""
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )

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
        Enrich a document's content with parent-child context.

        For PARENT documents: append child page summaries to content
        For CHILD documents: prepend parent context info
        """
        content = doc.get("content", "")
        doc_id = doc.get("id")
        parent_id = doc.get("parent_id")
        title = doc.get("title", "Untitled")

        enriched_parts = []

        # If this doc has a parent in our data, prepend parent context
        if parent_id and parent_id in id_to_doc:
            parent_doc = id_to_doc[parent_id]
            parent_title = parent_doc.get("title", "Untitled")
            enriched_parts.append(
                f"[Parent Page: {parent_title}]\n"
            )

        # Add the main content
        enriched_parts.append(content)

        # If this doc has children, append their summaries
        children = parent_to_children.get(doc_id, [])
        if children:
            enriched_parts.append("\n\n## Child Pages Summary")
            for child in children:
                child_title = child.get("title", "Untitled")
                child_content = child.get("content", "")
                # Take the first ~300 chars as a summary
                summary = child_content[:300].strip()
                if len(child_content) > 300:
                    summary += "..."
                enriched_parts.append(
                    f"\n### {child_title}\n{summary}"
                )

        return "\n".join(enriched_parts)

    def _process_document(self, doc, id_to_doc, parent_to_children):
        """Private method to chunk and format a single document with enriched context."""
        content = self._enrich_content(doc, id_to_doc, parent_to_children)
        if not content.strip():
            return [], [], []

        # Physical Split (Enforce Size Limits)
        # We skip MarkdownHeaderTextSplitter because it has a known bug of dropping 
        # unheadered text at the end of long documents.
        physical_splits = self.text_splitter.create_documents([content])

        # Merge very short chunks (< 50 chars) into the next chunk
        # This prevents tiny fragments like "Checkpoint #1 Slideshow" from
        # becoming standalone chunks that lack meaningful content.
        MIN_CHUNK_CHARS = 50
        merged_splits = []
        carry_over = ""
        for split in physical_splits:
            if len(split.page_content.strip()) < MIN_CHUNK_CHARS:
                carry_over += split.page_content + "\n"
            else:
                if carry_over:
                    split.page_content = carry_over + split.page_content
                    carry_over = ""
                merged_splits.append(split)
        # If there's leftover carry_over at the very end of the file
        if carry_over:
            if merged_splits:
                # Append the trailing short text to the last valid chunk
                merged_splits[-1].page_content += "\n" + carry_over.strip()
            elif physical_splits:
                # Edge case: the entire document was just one tiny <50 char string
                physical_splits[-1].page_content = carry_over.strip()
                merged_splits.append(physical_splits[-1])

        physical_splits = merged_splits
        chunks = []
        metadatas = []
        ids = []

        # Build parent_title for metadata
        parent_id = doc.get("parent_id")
        parent_title = None
        if parent_id and parent_id in id_to_doc:
            parent_title = id_to_doc[parent_id].get("title", "Untitled")

        # Format for ChromaDB
        for i, chunk in enumerate(physical_splits):
            chunks.append(chunk.page_content)
            
            chunk_metadata = {
                "parent_id": doc.get("id"),
                "title": doc.get("title", "Untitled"),
                "url": doc.get("url"),
                "source_type": doc.get("source_type", "page"),
                "chunk_index": i
            }

            # Add parent context to metadata for retrieval-time grouping
            if parent_title:
                chunk_metadata["parent_title"] = parent_title
            if parent_id:
                chunk_metadata["notion_parent_id"] = parent_id

            # Merge the Markdown headers extracted by LangChain
            chunk_metadata.update(chunk.metadata)
            
            metadatas.append(chunk_metadata)
            
            # Deterministic ID creation
            ids.append(f"{doc['id']}_{i}")

        return chunks, metadatas, ids

    def run_pipeline(self):
        """Public method to execute the full ingestion pipeline."""
        print(f"📂 Loading data from {self.file_path}...")
        raw_docs = self._load_data()
        # Build parent-child relationship maps
        print("🔗 Building parent-child relationship maps...")
        id_to_doc, parent_to_children = self._build_parent_child_maps(raw_docs)
        print(f"   Found {len(parent_to_children)} parent documents with children")
        all_chunks = []
        all_metadatas = []
        all_ids = []

        print(f"✂️  Running Hybrid Chunking on {len(raw_docs)} documents (with context enrichment)...")

        for doc in raw_docs:
            chunks, metadatas, ids = self._process_document(doc, id_to_doc, parent_to_children)
            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
            all_ids.extend(ids)

        if all_chunks:
            print(f"💾 Storing {len(all_chunks)} chunks into Chroma...")
            self.db.add_documents(all_chunks, all_metadatas, all_ids)
        else:
            print("⚠️ No chunks were created.")

# --- Execution ---
if __name__ == "__main__":
    # The instantiation is clean, and the parameters can easily be swapped for testing.
    ingestor = NotionIngestor(file_path="../../data/notion_data.json")
    ingestor.db.reset()
    ingestor.run_pipeline()

    # The teammate changed this test query, using their query instead.
    result = ingestor.db.query("What is the purpose of this document?", n_results=10)
    print("Query Results:", result["documents"][:1])
