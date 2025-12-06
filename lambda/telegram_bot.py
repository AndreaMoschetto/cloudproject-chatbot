import json
import os
import urllib.request
import boto3
import re

# from terraform
TOKEN = os.environ.get('TELEGRAM_TOKEN')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
ORCHESTRATOR_URL = os.environ.get('ORCHESTRATOR_URL', '')
ALLOWED_IDS = os.environ.get('ALLOWED_IDS', '').split(',')
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def sanitize_filename(filename):
    """Sostituisce spazi e caratteri non alfanumerici con underscore"""
    name, ext = os.path.splitext(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    clean_name = re.sub(r'_+', '_', clean_name)
    return f"{clean_name}{ext}"


def lambda_handler(event, context):
    print("Event received:", event)

    try:
        body = json.loads(event['body'])

        if 'message' in body:
            message = body['message']
            chat_id = message['chat']['id']

            # --- SOFT SECURITY BLOCK ---------------------------
            if ALLOWED_IDS and ALLOWED_IDS != [''] and chat_id not in ALLOWED_IDS:
                print(f"⛔ Unauthorized access attempt from Chat ID: {chat_id}")
                msg = (
                    "⛔ **ACCESS DENIED**\n"
                    "You are not authorized to use this bot.\n\n"
                    f"Your Chat ID is: `{chat_id}`\n"
                    "Send this code to the administrator to request access."
                )
                send_message(chat_id, msg)
                return {'statusCode': 200}
            # ---------------------------------------------------

            if 'document' in message:
                file_id = message['document']['file_id']
                raw_filename = message['document'].get('file_name', 'document.pdf')
                mime_type = message['document'].get('mime_type', '')

                if 'pdf' not in mime_type and not raw_filename.endswith('.pdf'):
                    send_message(chat_id, "⚠️ Accetto solo file PDF.")
                    return {'statusCode': 200}

                file_name = sanitize_filename(raw_filename)
                send_message(chat_id, f"⏳ Scarico: {file_name} ...")
                file_path = get_telegram_file_path(file_id)
                download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

                s3 = boto3.client('s3')
                with urllib.request.urlopen(download_url) as f:
                    s3.upload_fileobj(
                        f,
                        S3_BUCKET,
                        file_name,
                        ExtraArgs={"Metadata": {"chat_id": str(chat_id)}}
                    )
                send_message(chat_id, f"✅ File **{file_name}** loaded on S3!\nThe RAG system is processing it. I will notify you when it's done.")

            elif 'text' in message:
                text = message['text'].strip()

                if text == "/start":
                    msg = (
                        "Hello! 👋 I'm the CloudNLP bot.\n\n"
                        "📄 **Send a PDF** to upload it to the Knowledge Base.\n"
                        "📂 **/list** - See uploaded files\n"
                        "🗑️ **/delete <name>** - Delete a file"
                    )
                    send_message(chat_id, msg)

                elif text == "/list":
                    # Call the Orchestrator to get the list of files
                    if not ORCHESTRATOR_URL:
                        send_message(chat_id, "❌ Configuration error: ORCHESTRATOR_URL missing.")
                        return {'statusCode': 200}

                    try:
                        # Remove trailing slash from base URL
                        api_url = f"{ORCHESTRATOR_URL.rstrip('/')}/files"
                        req = urllib.request.Request(api_url)
                        with urllib.request.urlopen(req) as response:
                            data = json.loads(response.read())
                            files = data.get("files", [])
                            if files:
                                file_list = "\n".join([f"- `{f}`" for f in files])
                                send_message(chat_id, f"📂 **Files in the system:**\n{file_list}")
                            else:
                                send_message(chat_id, "📭 No files found.")
                    except Exception as e:
                        print(f"List error: {e}")
                        send_message(chat_id, f"❌ Error retrieving list: {e}")

                elif text.startswith("/delete"):
                    # Example command: /delete my_file.pdf
                    parts = text.split(maxsplit=1)
                    if len(parts) < 2:
                        send_message(chat_id, "⚠️ Usage: `/delete filename.pdf`")
                    else:
                        filename = parts[1].strip()
                        if not ORCHESTRATOR_URL:
                            send_message(chat_id, "❌ Configuration error: ORCHESTRATOR_URL missing.")
                            return {'statusCode': 200}

                        try:
                            api_url = f"{ORCHESTRATOR_URL.rstrip('/')}/files/{filename}"
                            # Create a DELETE request
                            req = urllib.request.Request(api_url, method='DELETE')
                            urllib.request.urlopen(req)
                            send_message(chat_id, f"🗑️ File **{filename}** deleted successfully.")
                        except urllib.error.HTTPError as e:
                            if e.code == 404:
                                send_message(chat_id, f"⚠️ File **{filename}** not found.")
                            else:
                                send_message(chat_id, f"❌ Deletion error: {e}")
                        except Exception as e:
                            send_message(chat_id, f"❌ Generic error: {e}")

                else:
                    send_message(chat_id, "Unrecognized command. Use /start for help.")

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
