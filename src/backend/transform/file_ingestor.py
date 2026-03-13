import hashlib

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from src.backend.load.chroma_manager import ChromaManager

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class FileIngestor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n```\n", "\n---", "\n- ", "\n", " ", ""],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        ext = self._get_extension(filename)

        if ext in (".txt", ".md"):
            return file_bytes.decode("utf-8")
        elif ext == ".pdf":
            return self._extract_pdf_text(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _extract_pdf_text(self, file_bytes: bytes) -> str:
        import io
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    def _get_extension(self, filename: str) -> str:
        return "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    def ingest(
        self, file_bytes: bytes, filename: str, user_id: int, chroma: ChromaManager
    ) -> dict:
        text = self.extract_text(file_bytes, filename)
        if not text.strip():
            return {"filename": filename, "chunk_count": 0}

        ext = self._get_extension(filename)
        # Use markdown-aware splitting for .md files, plain splitting otherwise
        if ext == ".md":
            md_splits = self.markdown_splitter.split_text(text)
            physical_splits = self.text_splitter.split_documents(md_splits)
            chunks = [s.page_content for s in physical_splits]
            split_metadatas = [s.metadata for s in physical_splits]
        else:
            chunks = self.text_splitter.split_text(text)
            split_metadatas = [{}] * len(chunks)

        # Deterministic file hash for stable IDs
        file_hash = hashlib.md5(file_bytes).hexdigest()[:8]

        metadatas = []
        ids = []
        for i, extra_meta in enumerate(split_metadatas):
            meta = {
                "source_type": "upload",
                "title": filename,
                "uploaded_by": str(user_id),
                "chunk_index": i,
            }
            meta.update(extra_meta)
            metadatas.append(meta)
            ids.append(f"upload_{file_hash}_{i}")

        chroma.add_documents(chunks, metadatas, ids)

        return {"filename": filename, "chunk_count": len(chunks)}
