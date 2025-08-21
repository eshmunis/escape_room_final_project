"""
This module loads the game world definition from a JSON file.

The world file describes:
- Rooms (names, descriptions, exits, items, puzzles)
- The starting room
- Items that can be interacted with

By default, it loads from "data/world.json".
"""

import json

def load_world(filepath="data/world.json"):
    """ 
    Load the game world data from a JSON file.

    Parameters:
        filepath (str, optional): Path to the JSON file that defines the world.
            Defaults to "data/world.json".

    Returns:
        dict: Parsed world data as a Python dictionary.

    Raises:
        FileNotFoundError: If the file cannot be found at the given path.
        json.JSONDecodeError: If the file is not valid JSON.

    Side Effects:
        Opens and reads from the specified file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)