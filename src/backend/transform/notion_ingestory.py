import json
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from src.backend.load.chroma_manager import ChromaManager

class NotionIngestor:
    def __init__(self, file_path="./notion_data.json", chunk_size=1000, chunk_overlap=200):
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

    def _process_document(self, doc):
        """Private method to chunk and format a single document."""
        content = doc.get("content", "")
        if not content:
            return [], [], []

        # Logical Split (Extract Headers)
        md_splits = self.markdown_splitter.split_text(content)

        # Physical Split (Enforce Size Limits)
        physical_splits = self.text_splitter.split_documents(md_splits)
        
        chunks = []
        metadatas = []
        ids = []

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
        
        all_chunks = []
        all_metadatas = []
        all_ids = []

        print(f"✂️  Running Hybrid Chunking on {len(raw_docs)} documents...")

        for doc in raw_docs:
            chunks, metadatas, ids = self._process_document(doc)
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
    ingestor = NotionIngestor(file_path="notion_data.json", chunk_size=1000)
    ingestor.db.reset()
    ingestor.run_pipeline()
