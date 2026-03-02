import json
import os

FILE_PATH = "data/chats.json"


def load_chats():
    # Ensure data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    # If file does not exist, create with empty dict
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}

    # If file exists but is empty or corrupted
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        # Reset corrupted file safely
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}


def save_chats(chats):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=2, ensure_ascii=False)