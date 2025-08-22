# Make sure to test with: python -m pytest tests/test_game.py

import time

from game import (
    GAME_TIME_LIMIT,
    time_left,
    format_mmss,
    build_rooms,
    handle_go,
)
from room import Room
from player import Player


def test_format_mmss_basic():
    assert format_mmss(0) == "0:00"
    assert format_mmss(59) == "0:59"
    assert format_mmss(61) == "1:01"
    # Negative gets clamped to 0
    assert format_mmss(-10) == "0:00"


def test_time_left_uses_monotonic_delta():
    start = time.monotonic()
    tl = time_left(start)
    # Allow up to ~1s drift due to execution time
    assert GAME_TIME_LIMIT - 1 <= int(tl) <= GAME_TIME_LIMIT


def test_build_rooms_creates_rooms_and_attaches_puzzles():
    world = {
        "rooms": {
            "foyer": {
                "description": "Entry",
                "exits": {"north": "hallway"},
                "items": ["flashlight"],
            },
            "hallway": {
                "description": "A long corridor",
                "exits": {"south": "foyer", "east": "study"},
                "items": [],
                "puzzle": "lockpad",
            },
            "study": {
                "description": "Dusty books",
                "exits": {"west": "hallway"},
                "items": [],
            },
        },
        "puzzles": {
            "lockpad": {
                "question": "Enter code:",
                "answer": "1234",
                "wrong_responses": ["Nope.", "Try again."],
            }
        },
        "items": {},
        "start_room": "foyer",
    }

    rooms = build_rooms(world)

    assert set(rooms.keys()) == {"foyer", "hallway", "study"}
    assert isinstance(rooms["foyer"], Room)
    assert "north" in rooms["foyer"].exits
    assert "flashlight" in rooms["foyer"].items

    # Puzzle normalized and attached
    hall = rooms["hallway"]
    assert hall.puzzle is not None
    assert hall.puzzle.get("question") == "Enter code:"
    assert hall.puzzle.get("answer") == "1234"
    # pattern key should exist (empty string if not provided)
    assert "pattern" in hall.puzzle
    # solved should default to False
    assert hall.puzzle.get("solved") is False
    # optional wrong_responses carried through
    assert hall.puzzle.get("wrong_responses") == ["Nope.", "Try again."]


def test_handle_go_requires_flashlight_from_foyer():
    # Setup a minimal map
    foyer = Room("foyer", "Entry", exits={"north": "hallway"}, items={"flashlight"})
    hallway = Room("hallway", "Corridor", exits={"south": "foyer"})
    rooms = {"foyer": foyer, "hallway": hallway}

    p = Player("foyer")
    # No flashlight in inventory -> should NOT move
    handle_go(p, rooms, ["north"])
    assert p.location == "foyer"


def test_handle_go_moves_when_flashlight_present():
    foyer = Room("foyer", "Entry", exits={"north": "hallway"}, items={"flashlight"})
    hallway = Room("hallway", "Corridor", exits={"south": "foyer"})
    rooms = {"foyer": foyer, "hallway": hallway}

    p = Player("foyer")
    p.add_item("flashlight")
    handle_go(p, rooms, ["north"])
    assert p.location == "hallway"