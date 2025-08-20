"""
Loads the game world definition from data/world.json.
"""

import json

def load_world(filepath="data/world.json"):
    """Return the world data as a Python dict.

    Raises:
        FileNotFoundError, json.JSONDecodeError
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)