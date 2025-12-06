import json
import urllib.request
import os
import boto3


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    # Reads the S3 event
    # It contains info about the uploaded file
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        print(f"New file detected: s3://{bucket_name}/{file_key}")

        chat_id = None
        try:
            response = s3.head_object(Bucket=bucket_name, Key=file_key)
            # S3 restituisce i metadata in lowercase
            chat_id = response.get('Metadata', {}).get('chat_id')
            print(f"Found Chat ID in metadata: {chat_id}")
        except Exception as e:
            print(f"Warning: Could not read metadata: {e}")

        # The RAG URL is passed as an environment variable from Terraform
        rag_api_url = os.environ['RAG_INGEST_API_URL']  # E.g., https://am-cloud.../ingest-s3

        payload = {
            "file_key": file_key,
            "chat_id": chat_id
        }

        # Calls the RAG Service (Webhook)
        try:
            req = urllib.request.Request(
                rag_api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            response = urllib.request.urlopen(req)
            print(f"RAG Service responded: {response.read().decode('utf-8')}")

        except Exception as e:
            print(f"Error calling RAG Service: {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent to RAG Service')
    }
