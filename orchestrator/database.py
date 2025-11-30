import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from abc import ABC, abstractmethod
from constants import USE_DYNAMODB


class ChatHistoryRepository(ABC):
    @abstractmethod
    def save_message(self, session_id: str, role: str, content: str):
        pass

    @abstractmethod
    def get_history(self, session_id: str):
        pass

# Implementation 1: Local JSON File


class LocalJsonRepository(ChatHistoryRepository):
    def __init__(self, filepath="chat_history.json"):
        self.filepath = filepath
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                json.dump({}, f)

    def _load_data(self):
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_data(self, data):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=4)

    def save_message(self, session_id: str, role: str, content: str):
        data = self._load_data()
        if session_id not in data:
            data[session_id] = []

        message_entry = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        data[session_id].append(message_entry)
        self._save_data(data)

    def get_history(self, session_id: str):
        data = self._load_data()
        return data.get(session_id, [])

#  Implementation 2: DynamoDB


class DynamoDBRepository(ChatHistoryRepository):
    def __init__(self, table_name, region_name="us-east-1"):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)

    def save_message(self, session_id: str, role: str, content: str):
        timestamp = datetime.now().isoformat()
        try:
            self.table.put_item(
                Item={
                    'session_id': session_id,  # Partition Key
                    'timestamp': timestamp,    # Sort Key
                    'role': role,
                    'content': content
                }
            )
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")

    def get_history(self, session_id: str):
        try:
            response = self.table.query(
                KeyConditionExpression=Key('session_id').eq(session_id)
            )
            items = response.get('Items', [])
            items.sort(key=lambda x: x['timestamp'])
            return items
        except Exception as e:
            print(f"Error reading from DynamoDB: {e}")
            return []


def get_repository():
    if USE_DYNAMODB.lower() == "true":
        table_name = os.getenv("DYNAMODB_TABLE", "cloud-nlp-history")
        return DynamoDBRepository(table_name)

    return LocalJsonRepository()
