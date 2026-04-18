# ChromaDB native s390x build using python slim
FROM python:3.11-slim

# Install system dependencies required for native s390x compilation of C-bindings
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /chroma

# Compiling chromadb and pulling core dependencies
RUN pip install --no-cache-dir chromadb uvicorn

EXPOSE 8000

# Set ChromaDB backend storage configurations
ENV IS_PERSISTENT=TRUE
ENV PERSIST_DIRECTORY=/chroma/chroma

# Initialize via Uvicorn 
CMD ["uvicorn", "chromadb.app:app", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]
