import json
import os
from datetime import datetime
from abc import ABC, abstractmethod


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
    def __init__(self, table_name):
        pass

    def save_message(self, session_id: str, role: str, content: str):
        pass

    def get_history(self, session_id: str):
        pass


def get_repository():
    if os.getenv("USE_DYNAMODB") == "true":
        return DynamoDBRepository(os.getenv("DYNAMODB_TABLE", "ChatHistory"))
    return LocalJsonRepository()
