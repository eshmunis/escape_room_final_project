# Make sure to test with: python -m pytest tests/test_room.py

from room import Room

def test_init_defaults_and_available_exits():
    r = Room(name="foyer", description="A chilly entryway.")
    assert r.name == "foyer"
    assert r.description.startswith("A chilly")
    assert isinstance(r.exits, dict) and r.exits == {}
    assert isinstance(r.items, set) and len(r.items) == 0
    assert r.visited is False
    assert r.puzzle is None
    # With no exits, message should say so
    assert "no visible exits" in r.available_exits_text().lower()


def test_add_exit_and_get_exit_case_insensitive():
    r = Room("hallway", "Long and narrow.")
    r.add_exit("North", "study")
    r.add_exit("east", "kitchen")
    assert r.get_exit("north") == "study"
    assert r.get_exit("EAST") == "kitchen"
    txt = r.available_exits_text().lower()
    assert "exits:" in txt and "east" in txt and "north" in txt


def test_add_remove_item_and_has_item():
    r = Room("study", "Dusty books.")
    r.add_item("flashlight")
    assert r.has_item("flashlight") is True
    r.remove_item("flashlight")
    assert r.has_item("flashlight") is False


def test_remove_item_raises_value_error_when_missing():
    r = Room("study", "Dusty books.")
    try:
        r.remove_item("ghost-key")
        assert False, "Expected ValueError when removing missing item"
    except ValueError:
        assert True


def test_items_text_variants_items_present_and_no_items_paths():
    # Items present
    r1 = Room("foyer", "desc", items={"note"})
    msg1 = r1.items_text().lower()
    assert "you see" in msg1 and "note" in msg1

    # No items, puzzle present and unsolved -> generic hint mentioning 'solve'
    r2 = Room("lockroom", "desc", puzzle={"question": "Code?", "answer": "123"})
    msg2 = r2.items_text().lower()
    assert "solve" in msg2

    # No items, no puzzle -> nothing useful
    r3 = Room("empty", "desc")
    msg3 = r3.items_text().lower()
    assert "nothing useful" in msg3


def test_try_solve_puzzle_exact_and_repeat_flow():
    r = Room("door", "desc", puzzle={"question": "Code?", "answer": "429"})
    ok_wrong, msg_wrong = r.try_solve_puzzle("111")
    assert ok_wrong is False and "not the correct" in msg_wrong.lower()
    ok_right, msg_right = r.try_solve_puzzle("429")
    assert ok_right is True and "solved" in msg_right.lower()
    # Solving again should report already solved
    ok_again, msg_again = r.try_solve_puzzle("anything")
    assert ok_again is True and "already solved" in msg_again.lower()


def test_try_solve_puzzle_regex_and_describe_combo():
    # Regex accepts exactly three digits
    r = Room("vault", "Steel walls.", puzzle={"question": "3 digits", "pattern": r"^\d{3}$"})

    # Before solving, with no items, items_text should nudge toward 'solve'
    pre = r.items_text().lower()
    assert "solve" in pre

    # Wrong attempt first
    bad, msg = r.try_solve_puzzle("12a")
    assert bad is False and "format" in msg.lower()

    # Now a correct attempt
    ok, _ = r.try_solve_puzzle("123")
    assert ok is True

    # After solving, items_text should no longer give the puzzle hint
    post = r.items_text().lower()
    assert "nothing useful" in post

    # Any later attempt reports already solved
    again, msg2 = r.try_solve_puzzle("000")
    assert again is True and "already solved" in msg2.lower()