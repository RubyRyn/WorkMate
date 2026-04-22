import os
import json
import boto3
import time
from datetime import datetime, timezone
import urllib3

# Constants
SSM_PARAM_PREFIX = "/workmate/"
SQS_QUEUE_URL_PARAM = SSM_PARAM_PREFIX + "SQS_QUEUE_URL"
NOTION_TOKEN_PARAM = SSM_PARAM_PREFIX + "NOTION_TOKEN"
LAST_SYNC_TIME_PARAM = SSM_PARAM_PREFIX + "LAST_SYNC_TIME"

ssm = boto3.client('ssm')
sqs = boto3.client('sqs')
http = urllib3.PoolManager()

def get_param(name):
    try:
        return ssm.get_parameter(Name=name, WithDecryption=True)['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        return None

def set_param(name, value):
    ssm.put_parameter(Name=name, Value=value, Type='String', Overwrite=True)

def lambda_handler(event, context):
    """
    Triggered by EventBridge. 
    Checks Notion for updated pages since LAST_SYNC_TIME and pushes IDs to SQS.
    
    Note: This detector uses a single system-wide Notion integration token 
    (from SSM) to monitor a shared/public workspace. This is distinct from 
    the main application, which uses per-user OAuth tokens for multi-tenant 
    private workspace access.
    """
    try:
        notion_token = get_param(NOTION_TOKEN_PARAM)
        queue_url = get_param(SQS_QUEUE_URL_PARAM)
        
        if not notion_token or not queue_url:
            print("Missing Notion Token or SQS Queue URL in SSM.")
            return {'statusCode': 400, 'body': "Missing configuration"}

        last_sync_str = get_param(LAST_SYNC_TIME_PARAM)
        if last_sync_str:
            last_sync = datetime.fromisoformat(last_sync_str.replace('Z', '+00:00'))
        else:
            # Default to 1 hour ago if not set
            last_sync = datetime.fromtimestamp(time.time() - 3600, tz=timezone.utc)
            
        print(f"Checking for updates since {last_sync.isoformat()}")
        
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }
        
        url = "https://api.notion.com/v1/search"
        new_sync_time = datetime.now(timezone.utc)
        
        has_more = True
        next_cursor = None
        updated_page_ids = []
        
        while has_more:
            payload = {
                "sort": {
                    "direction": "descending",
                    "timestamp": "last_edited_time"
                }
            }
            if next_cursor:
                payload["start_cursor"] = next_cursor
                
            response = http.request(
                "POST", 
                url, 
                headers=headers, 
                body=json.dumps(payload).encode('utf-8')
            )
            
            if response.status != 200:
                print(f"Notion API error: {response.status} - {response.data.decode('utf-8')}")
                break
                
            data = json.loads(response.data.decode('utf-8'))
            
            for result in data.get("results", []):
                last_edited_str = result.get("last_edited_time")
                if not last_edited_str:
                    continue
                
                last_edited = datetime.fromisoformat(last_edited_str.replace('Z', '+00:00'))
                
                if last_edited > last_sync:
                    updated_page_ids.append(result["id"])
                else:
                    # Results are sorted descending, so we can stop
                    has_more = False
                    break
            
            if has_more:
                has_more = data.get("has_more", False)
                next_cursor = data.get("next_cursor")
        
        print(f"Found {len(updated_page_ids)} updated pages.")
        
        # Batch send to SQS (max 10 per batch)
        for i in range(0, len(updated_page_ids), 10):
            batch = updated_page_ids[i:i+10]
            entries = [
                {'Id': str(j), 'MessageBody': page_id}
                for j, page_id in enumerate(batch)
            ]
            sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
            
        # Update last sync time
        set_param(LAST_SYNC_TIME_PARAM, new_sync_time.isoformat())
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully queued {len(updated_page_ids)} pages.")
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
