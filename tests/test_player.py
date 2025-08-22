# Make sure to test with: python -m pytest tests/test_player.py

import pytest
from player import Player

def test_move_to_changes_location():
    p = Player("start")
    p.move_to("kitchen")
    assert p.location == "kitchen"

def test_add_and_has_item():
    p = Player("start")
    p.add_item("key")
    assert p.has_item("key") is True

def test_remove_item_success():
    p = Player("start")
    p.add_item("key")
    p.remove_item("key")
    assert not p.has_item("key")

def test_remove_item_raises_error():
    p = Player("start")
    with pytest.raises(ValueError):
        p.remove_item("ghost")

def test_list_inventory_empty_and_nonempty():
    p = Player("start")
    assert "not carrying anything" in p.list_inventory().lower()
    p.add_item("map")
    result = p.list_inventory()
    assert "map" in result
    assert "carrying" in result