"""
Defines the Room class (name, description, exits, items, optional puzzle).
- exits: dict mapping directions (e.g., "north") -> room name
- items: set of item names present in the room
- puzzle (optional): dict with:
    {"question": str, "answer": str, "solved": bool}
  OR {"question": str, "pattern": str, "solved": bool} for regex puzzles
"""

import re


class Room:
    """Represents a location in the game world."""

    def __init__(self, name, description, exits=None, items=None, puzzle=None):
        self.name = name
        self.description = description
        self.exits = exits or {}
        self.items = items or set()
        self.puzzle = None
        if puzzle:
            p = dict(puzzle)
            if "solved" not in p:
                p["solved"] = False
            self.puzzle = p

    # Exits 
    def add_exit(self, direction, room_name):
        """Add or update an exit from this room."""
        self.exits[direction.lower()] = room_name

    def get_exit(self, direction):
        """Return the room name in the given direction, or None."""
        return self.exits.get(direction.lower())

    def available_exits_text(self):
        """Return a friendly string of available exits."""
        if not self.exits:
            return "There are no visible exits."
        dirs = ", ".join(sorted(self.exits.keys()))
        return "Exits: " + dirs

    # Items
    def add_item(self, item):
        """Place an item in the room."""
        self.items.add(item)

    def remove_item(self, item):
        """Remove an item from the room.

        Raises:
            ValueError: If the item is not present.
        """
        if item not in self.items:
            raise ValueError("There is no '{}' here.".format(item))
        self.items.remove(item)

    def has_item(self, item):
        """Return True if the room contains the item."""
        return item in self.items

    def items_text(self):
        """Return a friendly list of items in the room."""
        if not self.items:
            return "You see nothing useful here."
        return "You see: " + ", ".join(sorted(self.items))

    # Puzzle
    def has_puzzle(self):
        return bool(self.puzzle) and not self.puzzle.get("solved")

    def puzzle_question(self):
        if not self.puzzle:
            return None
        return self.puzzle.get("question")

    def try_solve_puzzle(self, user_answer):
        """Attempt to solve the puzzle with the given answer.

        Returns:
            (success, message)
        """
        if not self.puzzle:
            return False, "There is no puzzle here."

        if self.puzzle.get("solved"):
            return True, "The puzzle is already solved."

        # Regex pattern mode
        if "pattern" in self.puzzle:
            if re.fullmatch(self.puzzle["pattern"], user_answer.strip(), flags=re.IGNORECASE):
                self.puzzle["solved"] = True
                return True, "You solved the puzzle!"
            return False, "That doesn't match the required format."

        # Exact answer mode
        expected = self.puzzle.get("answer", "").strip().lower()
        if user_answer.strip().lower() == expected and expected != "":
            self.puzzle["solved"] = True
            return True, "You solved the puzzle!"
        return False, "That's not the correct answer."

    # Description
    def describe(self):
        """Return a full description of the room, including exits and items."""
        parts = [self.description, self.items_text(), self.available_exits_text()]
        return "\n".join(parts)