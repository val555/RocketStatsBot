import json
import os
from pathlib import Path
from typing import List

HISTORY_FILE = Path('data/history.json')
MAPPINGS_FILE = Path('data/mappings.json')

def save_player_stats(discord_id: str, stats: dict) -> None:
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    history = load_history()
    history.setdefault(discord_id, []).append(stats)
    HISTORY_FILE.write_text(json.dumps(history))

def load_history() -> dict:
    return json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else {}

def register_player(discord_id: str, rl_username: str) -> None:
    mappings = load_mappings()
    mappings[discord_id] = rl_username
    MAPPINGS_FILE.write_text(json.dumps(mappings))

def load_mappings() -> dict:
    return json.loads(MAPPINGS_FILE.read_text()) if MAPPINGS_FILE.exists() else {}