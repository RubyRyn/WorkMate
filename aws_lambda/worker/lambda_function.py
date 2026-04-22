import os
import json
import boto3
import sys

# Ensure the root of the project is in the path for imports to work in Lambda
# This assumes the deployment package contains the 'src' directory.
sys.path.append(os.path.join(os.getcwd()))

try:
    from src.backend.load.chroma_manager import ChromaManager
    from src.backend.transform.notion_ingestory import NotionIngestor
    from src.Notion.notion_fetcher.client import NotionClient
    from src.Notion.notion_fetcher.fetchers.page_fetcher import PageFetcher
except ImportError as e:
    print(f"Import Error: {e}")
    # In a real Lambda environment, we need to ensure the src directory is packaged correctly.

# Constants
SSM_PARAM_PREFIX = "/workmate/"
NOTION_TOKEN_PARAM = SSM_PARAM_PREFIX + "NOTION_TOKEN"
CHROMA_HOST_PARAM = SSM_PARAM_PREFIX + "CHROMA_HOST"
CHROMA_PORT_PARAM = SSM_PARAM_PREFIX + "CHROMA_PORT"

ssm = boto3.client('ssm')

def get_param(name):
    try:
        return ssm.get_parameter(Name=name, WithDecryption=True)['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        return None

def lambda_handler(event, context):
    """
    Triggered by SQS. Fetches content for page_ids, chunks them, and stores in Chroma.
    Batch size is typically 10.
    """
    try:
        notion_token = get_param(NOTION_TOKEN_PARAM)
        chroma_host = get_param(CHROMA_HOST_PARAM)
        chroma_port = get_param(CHROMA_PORT_PARAM) or "8000"
        
        if not notion_token:
            print("Missing Notion Token in SSM.")
            return {'statusCode': 400, 'body': "Missing configuration"}

        # Set environment variables so ChromaManager (which uses os.getenv) can find the cluster
        if chroma_host:
            os.environ["CHROMA_HOST"] = chroma_host
            os.environ["CHROMA_PORT"] = chroma_port
            print(f"Configured Chroma HttpClient to {chroma_host}:{chroma_port}")
            
        client = NotionClient(notion_token)
        fetcher = PageFetcher(client)
        ingestor = NotionIngestor() 
        
        processed_count = 0
        failed_ids = []
        records = event.get('Records', [])
        print(f"Received batch of {len(records)} records from SQS.")

        for record in records:
            page_id = record['body']
            print(f"Processing page: {page_id}")
            
            try:
                # 1. Fetch full page content (metadata + block content)
                doc = fetcher.fetch_page(page_id)
                if not doc:
                    print(f"  Page {page_id} has no content or could not be fetched.")
                    continue
                    
                # 2. Convert NotionDocument model to dict for the ingestor
                doc_dict = doc.to_dict()
                
                # 3. Chunk the document
                # Returns (all_chunks, all_metadatas, all_ids)
                chunks, metas, ids = ingestor.chunk_documents([doc_dict])
                
                if chunks:
                    print(f"  Storing {len(chunks)} chunks in Chroma...")
                    # 4. Upsert into ChromaDB (HttpClient)
                    ingestor.db.add_documents(chunks, metas, ids)
                    processed_count += 1
                else:
                    print(f"  No content found for {page_id} after chunking.")
                    
            except Exception as e:
                print(f"  Error processing page {page_id}: {e}")
                # Track failed records for partial batch failure
                failed_ids.append({'itemIdentifier': record['messageId']})
                continue
                
        print(f"Batch completed. Processed {processed_count}/{len(records)} pages.")
        
        # Return batchItemFailures so SQS retries only failed messages
        response = {
            'statusCode': 200,
            'body': json.dumps(f"Processed {processed_count} pages.")
        }
        if failed_ids:
            response['batchItemFailures'] = failed_ids
            
        return response
        
    except Exception as e:
        print(f"Critical Worker Error: {e}")
        # Raising triggers SQS retry mechanism
        raise e
