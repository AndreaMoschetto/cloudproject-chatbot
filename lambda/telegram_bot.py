import json
import os
import urllib.request
import boto3

TOKEN = os.environ['TELEGRAM_TOKEN']
S3_BUCKET = os.environ['S3_BUCKET_NAME']
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def lambda_handler(event, context):
    print("Event received:", event)

    try:
        body = json.loads(event['body'])

        # Manage incoming messages
        if 'message' in body:
            message = body['message']
            chat_id = message['chat']['id']

            # CASE 1: It's a Document (PDF, etc.)
            if 'document' in message:
                file_id = message['document']['file_id']
                file_name = message['document'].get('file_name', 'document.pdf')
                mime_type = message['document'].get('mime_type', '')

                # Quick filter: only accept PDFs
                if 'pdf' not in mime_type and not file_name.endswith('.pdf'):
                    send_message(chat_id, "⚠️ I only accept PDF files.")
                    return {'statusCode': 200}

                send_message(chat_id, "⏳ Downloading the file...")

                # 1. Request the file path from Telegram
                file_path = get_telegram_file_path(file_id)

                # 2. Build the download URL
                download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

                # 3. Download from Telegram and upload to S3 (Direct streaming)
                s3 = boto3.client('s3')
                with urllib.request.urlopen(download_url) as f:
                    s3.upload_fileobj(f, S3_BUCKET, file_name)

                send_message(chat_id, f"✅ File **{file_name}** uploaded to S3!\nThe RAG system is analyzing it.")

            # CASE 2: It's just text
            elif 'text' in message:
                text = message['text']
                if text == "/start":
                    send_message(chat_id, "Hello! 👋\nSend me a PDF file and I'll add it to the Chatbot's knowledge.")
                else:
                    send_message(chat_id, "I don't speak much. Send me a PDF!")

        return {'statusCode': 200}

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500}


def get_telegram_file_path(file_id):
    """Calls getFile to obtain the remote path on the Telegram server"""
    url = f"{BASE_URL}/getFile?file_id={file_id}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode('utf-8'))
    return data['result']['file_path']


def send_message(chat_id, text):
    """Sends a message to the user"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Failed to send message: {e}")
