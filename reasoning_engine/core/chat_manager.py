import json
import os
from datetime import datetime
from typing import List, Dict, Any

class ChatManager:
    def __init__(self, history_file: str = "reasoning_engine/data/chat_history.json"):
        self.history_file = history_file
        self.messages = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(self.messages, f, indent=4)

    def add_message(self, msg_type: str, content: str, sender: str = "System"):
        """
        msg_type: 'tool', 'ai', 'user'
        """
        message = {
            "type": msg_type,
            "sender": sender,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.messages.append(message)
        self.save_history()

    def get_last_n(self, n: int = 10) -> List[Dict[str, Any]]:
        return self.messages[-n:]

    def clear(self):
        self.messages = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
