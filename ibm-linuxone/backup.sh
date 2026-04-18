#!/bin/sh
set -e

DATE=$(date +%Y-%m-%d_%H-%M-%S)
echo "Starting LinuxONE backup routine at $DATE"

ARCHIVE_DIR="/tmp/backups/$DATE"
mkdir -p "$ARCHIVE_DIR"

# 1. Dump PostgreSQL natively using pg_dump
echo "Dumping PostgreSQL database [workmate]..."
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -F c -d workmate > "$ARCHIVE_DIR/workmate_db.dump"

# 2. Archive ChromaDB Data Directory
echo "Zipping ChromaDB data directory..."
# We have read-only access to /chroma/chroma via docker-compose volumes
cd /chroma/chroma && zip -r "$ARCHIVE_DIR/chroma_data.zip" .

# 3. Stream sync to AWS S3 utilizing AWS CLI
echo "Uploading encrypted backup to s3://${S3_BACKUP_BUCKET}..."
aws s3 cp "$ARCHIVE_DIR" "s3://$S3_BACKUP_BUCKET/$DATE/" --recursive

# 4. Erase transient local archives
rm -rf "$ARCHIVE_DIR"

echo "LinuxONE Data Backups successfully completed and dispatched to S3!"
