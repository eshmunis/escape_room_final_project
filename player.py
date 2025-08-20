"""
Defines the Player class for the Escape Room game.
Tracks the player's current location and inventory.
"""

class Player:
    """Represents the player and their state in the game.

    Attributes:
        location (str): The name of the current room.
        inventory (set[str]): Items the player is carrying.
    """

    def __init__(self, start_location: str):
        """Initialize a new player at the given starting room."""
        self.location = start_location
        self.inventory = set()

    # Location 
    def move_to(self, room_name: str) -> None:
        """Move the player to a different room."""
        self.location = room_name

    # Inventory
    def add_item(self, item: str) -> None:
        """Add an item to the player's inventory."""
        self.inventory.add(item)

    def remove_item(self, item: str) -> None:
        """Remove an item from the inventory.

        Raises:
            ValueError: If the item is not in the inventory.
        """
        if item not in self.inventory:
            raise ValueError(f"'{item}' is not in your inventory.")
        self.inventory.remove(item)

    def has_item(self, item: str) -> bool:
        """Return True if the player has the item."""
        return item in self.inventory

    def list_inventory(self) -> str:
        """Return a friendly string listing carried items."""
        if not self.inventory:
            return "You are not carrying anything."
        items = ", ".join(sorted(self.inventory))
        return f"You are carrying: {items}"