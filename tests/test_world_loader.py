# Make sure to test with: python -m pytest tests/test_world_loader.py

import json
import os
from world_loader import load_world

def test_load_world_reads_valid_json(tmp_path=None):
    # Minimal valid world structure
    world_data = {
        "rooms": {
            "foyer": {
                "description": "a test room",
                "exits": {},
                "items": [],
                "puzzle": None
            }
        },
        "items": {},
        "puzzles": {},
        "start_room": "foyer"
    }

    # Write it to a temp file if pytest gives tmp_path, else current dir
    filename = "test_world.json"
    if tmp_path is not None:
        filepath = tmp_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(world_data, f)
        loaded = load_world(str(filepath))
    else:
        filepath = filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(world_data, f)
        try:
            loaded = load_world(filepath)
        finally:
            try:
                os.remove(filepath)
            except OSError:
                pass

    # Assertions: dict with correct keys
    assert isinstance(loaded, dict)
    assert "rooms" in loaded and "foyer" in loaded["rooms"]
    assert loaded["start_room"] == "foyer"