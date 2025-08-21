"""
This module defines the Player class used in the Escape Room game.

The Player tracks their current location in the game world and the items
they are carrying. It provides methods for moving between rooms and
managing inventory.
"""

class Player:
    """ 
    Represents the player and their state in the game.

    Attributes:
        location (str): The name of the current room where the player is located.
        inventory (set[str]): Items the player is carrying. A set is used so
            items are unique and can be checked quickly.
    """

    def __init__(self, start_location: str):
        """
        Initialize a new player at the given starting room.
        """
        self.location = start_location
        # Using a set makes it fast to check items and prevents duplicates
        self.inventory = set()

    # Location 
    def move_to(self, room_name: str) -> None:
        """ 
        Move the player to a different room.
        """
        self.location = room_name

    # Inventory
    def add_item(self, item: str) -> None:
        """ 
        Add an item to the player's inventory.
        """
        self.inventory.add(item)

    def remove_item(self, item: str) -> None:
        """
        Remove an item from the inventory.

        Raises:
            ValueError: If the item is not in the inventory.
        """
        if item not in self.inventory:
            # Better to raise an error than fail silently, so the player knows what went wrong
            raise ValueError(f"'{item}' is not in your inventory.")
        self.inventory.remove(item)

    def has_item(self, item: str) -> bool:
        """ 
        Check if the player has a specific item.
        """
        return item in self.inventory

    def list_inventory(self) -> str:
        """ 
        Return a friendly string listing carried items.
        """
        if not self.inventory:
            return "You are not carrying anything."
        items = ", ".join(sorted(self.inventory))
        return f"You are carrying: {items}"