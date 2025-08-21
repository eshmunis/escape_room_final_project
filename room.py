"""
This module defines the Room class, which represents a location
in the Escape Room game.

A Room has:
- A name and description
- Exits to other rooms (dict: direction -> room name)
- Items placed inside it (set of item names)
- An optional puzzle the player must solve to progress

Puzzle formats:
    {"question": str, "answer": str, "solved": bool}
or
    {"question": str, "pattern": str, "solved": bool}  # regex-based answer

Rooms handle their own description text, items, exits, and puzzle logic.
"""

import re


class Room:
    """ 
    Represents a location in the Escape Room game. 

    A Room keeps track of its description, connected exits, any items placed
    inside it, and (optionally) a puzzle the player must solve.

    Attributes:
        name (str): The name of the room.
        description (str): A short description of the room’s appearance or purpose.
        exits (dict[str, str]): Directions (like "north") mapped to room names.
        items (set[str]): Items currently present in the room.
        original_items (set[str]): Copy of the initial items, useful for resets or checks.
        visited (bool): Whether the player has entered the room before.
        puzzle (dict | None): Optional puzzle data. Can contain:
            - "question" (str): The puzzle question or prompt.
            - "answer" (str): The correct answer for exact matches.
            - "pattern" (str): Regex pattern for more flexible matching.
            - "solved" (bool): Whether the puzzle has been solved yet.
    """

    def __init__(self, name, description, exits=None, items=None, puzzle=None):
        """
        Initialize a new Room.

        Parameters:
            name (str): The name of the room.
            description (str): A description of the room.
            exits (dict[str, str], optional): Directions mapped to room names.
            items (set[str], optional): Items initially present in the room.
            puzzle (dict, optional): Puzzle data, if this room has one.

        Returns:
            None

        Side Effects:
            Sets up default exits, items, and puzzle state if not provided.
        """
        self.name = name
        self.description = description
        self.exits = exits or {}
        self.items = items or set()
        
        self.original_items = set(self.items) 
        self.visited = False 

        self.puzzle = None
        if puzzle:
            p = dict(puzzle)
            if "solved" not in p:
                p["solved"] = False
            self.puzzle = p

    # Exits 
    def add_exit(self, direction, room_name):
        """
        Add or update an exit from this room.

        Parameters:
            direction (str): Direction like "north" or "east".
            room_name (str): The name of the room in that direction.

        Returns:
            None

        Side Effects:
            Updates the exits dictionary for this room.
        """
        self.exits[direction.lower()] = room_name

    def get_exit(self, direction):
        """
        Get the room name connected in a given direction.

        Parameters:
            direction (str): Direction to check.

        Returns:
            str | None: The connected room name, or None if no exit exists.
        """
        return self.exits.get(direction.lower())

    def available_exits_text(self):
        """
        Return a user-friendly string listing available exits.

        Parameters:
            None

        Returns:
            str: Text describing the exits, or a message if none exist.
        """
        if not self.exits:
            return "There are no visible exits."
        dirs = ", ".join(sorted(self.exits.keys()))
        return "Exits: " + dirs

    # Items
    def add_item(self, item):
        """
        Place an item in the room.

        Parameters:
            item (str): The item to add.

        Returns:
            None

        Side Effects:
            Updates the items set for the room.
        """
        self.items.add(item)

    def remove_item(self, item):
        """
        Remove an item from the room.

        Parameters:
            item (str): The item to remove.

        Returns:
            None

        Raises:
            ValueError: If the item is not present in the room.

        Side Effects:
            Updates the items set by removing the specified item.
        """
        if item not in self.items:
            # Raising here avoids silent failures and gives the player feedback
            raise ValueError("There is no '{}' here.".format(item))
        self.items.remove(item)

    def has_item(self, item):
        """
        Check if the room contains a given item.

        Parameters:
            item (str): The item to check.

        Returns:
            bool: True if the item is in the room, False otherwise.
        """
        return item in self.items

    def items_text(self):
        """ 
        Return a user-friendly string of items in the room.

        Parameters:
            None

        Returns:
            str: A message listing visible items or puzzle hints.
        """
        if self.items:
            return "You see: " + ", ".join(sorted(self.items))
        # If no items, but a puzzle exists and isn’t solved, drop a generic hint
        if self.puzzle and not self.puzzle.get("solved", False):
        # Generic puzzle hint
            return "How can you solve this? Maybe try typing 'solve'."
            # If I want room-specific hints later, I could do:
            # if self.name.lower() == "hallway":
            #     return "That door looks like it needs a code. Try 'solve'."
            # if self.name.lower() == "study":
            #     return "It’s so dark... a light might help. Then try 'solve'."
        return "You see nothing useful here."

    # Puzzle
    def has_puzzle(self):
        """
        Check if the room has an unsolved puzzle.

        Parameters:
            None

        Returns:
            bool: True if an unsolved puzzle exists, False otherwise.
        """
        return bool(self.puzzle) and not self.puzzle.get("solved")

    def puzzle_question(self):
        """
        Get the puzzle’s question.

        Parameters:
            None

        Returns:
            str | None: The puzzle question, or None if no puzzle exists.
        """
        if not self.puzzle:
            return None
        return self.puzzle.get("question")

    def try_solve_puzzle(self, user_answer):
        """
        Attempt to solve the puzzle with the given answer.

        Parameters:
            user_answer (str): The player's attempt at solving the puzzle.

        Returns:
            tuple[bool, str]: A success flag and a feedback message.

        Side Effects:
            If solved, updates the puzzle’s "solved" field to True.
        """
        if not self.puzzle:
            return False, "There is no puzzle here."

        if self.puzzle.get("solved"):
            return True, "The puzzle is already solved."

        # Regex pattern mode
        pattern = self.puzzle.get("pattern")
        if pattern:
            if re.fullmatch(pattern, user_answer.strip(), flags=re.IGNORECASE):
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
        """ 
        Return a full description of the room, including exits and items.

        Parameters:
            None

        Returns:
            str: A description combining the room’s text, items, and exits.
        """
        parts = [self.description, self.items_text(), self.available_exits_text()]
        return "\n".join(parts)