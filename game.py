"""
game.py
--------
Connects the pieces: loads world.json, builds Room objects, creates Player,
and runs the main command loop (go/take/look/inventory/solve/help/quit).
"""

import random
from world_loader import load_world
from room import Room
from player import Player


# World construction helpers

def build_rooms(world_data):
    """Turn the JSON data into Room objects."""
    rooms = {}
    puzzles = world_data.get("puzzles", {})

    # First pass: create Room objects without puzzles attached
    for room_name, r in world_data.get("rooms", {}).items():
        rooms[room_name] = Room(
            name=room_name,
            description=r.get("description", ""),
            exits=r.get("exits", {}),
            items=set(r.get("items", [])),
            puzzle=None
        )

    # Second pass: attach puzzle dicts (if any)
    for room_name, r in world_data.get("rooms", {}).items():
        puzzle_id = r.get("puzzle")
        if puzzle_id:
            p = puzzles.get(puzzle_id, None)
            if p:
                # Normalize keys to match Room.try_solve_puzzle: "answer" or "pattern"
                pdict = {
                    "question": p.get("question", ""),
                    "answer": p.get("answer", ""),
                    "pattern": p.get("pattern", ""),  
                    "solved": False,
                }
                # Optional spooky feedback on wrong answers
                if "wrong_responses" in p:
                    pdict["wrong_responses"] = p["wrong_responses"]
                rooms[room_name].puzzle = pdict

    return rooms


def describe_current_room(player, rooms):
    """Print the current room description."""
    room = rooms[player.location]
    print("\n=== {} ===".format(room.name.capitalize()))
    print(room.describe())


# Command handlers

def handle_go(player, rooms, args):
    if not args:
        print("Go where? Try: go north / go south / go east / go west")
        return
    direction = args[0].lower()
    current = rooms[player.location]
    next_room_name = current.get_exit(direction)
    if not next_room_name:
        print("You can’t go {} from here.".format(direction))
        return
    
    if current.has_puzzle() and not current.puzzle.get("solved"):
        if current.name == "hallway" and direction == "east":
            print("The door is still locked. Maybe the keypad code opens it.")
            return
        
    player.move_to(next_room_name)
    describe_current_room(player, rooms)


def handle_take(player, rooms, args):
    if not args:
        print("Take what? Example: take key")
        return
    item = args[0].lower()
    room = rooms[player.location]
    if not room.has_item(item):
        print("There is no '{}' here.".format(item))
        return
    room.remove_item(item)
    player.add_item(item)
    print("You picked up the {}.".format(item))

def handle_inspect(player, rooms, world_items, args):
    if not args:
        print("Inspect what? Example: inspect flashlight")
        return
    item = args[0].lower()

    # Player must either have the item or it must be in the current room
    room = rooms[player.location]
    if not (player.has_item(item) or room.has_item(item)):
        print("You don’t see a '{}' here or in your inventory.".format(item))
        return

    # Pull description from world.json
    details = world_items.get(item)
    if details:
        print(details.get("description", "It looks ordinary."))
    else:
        print("You inspect the {}, but don’t notice anything special.".format(item))


def handle_inventory(player):
    print(player.list_inventory())


def handle_look(player, rooms):
    describe_current_room(player, rooms)


def handle_help():
    print("Commands you can try:")
    print("  look           - describe the room again")
    print("  go <dir>       - move (north/south/east/west)")
    print("  take <item>    - pick something up")
    print("  inspect <item>   - examine an item in detail")
    print("  inventory      - show what you’re carrying")
    print("  solve          - attempt the current room’s puzzle (if any)")
    print("  help           - this help")
    print("  quit           - exit the game")


def handle_solve(player, rooms):
    room = rooms[player.location]
    if not room.has_puzzle():
        print("There’s nothing to solve here.")
        return

    print(room.puzzle_question())
    answer = input("> ").strip()

    success, message = room.try_solve_puzzle(answer)
    if success:
        print(message)
        # Optional: Win condition if we’re in the final room & solved
        if player.location == "study":
            print("\nThe window gives way. Cold night air rushes in.")
            print("You crawl out, drop to the grass, and sprint away.")
            print("You escaped the house. Nice work!")
            return "WIN"
    else:
        # If the puzzle defines spooky wrong responses, pick one
        wr = None
        if room.puzzle and "wrong_responses" in room.puzzle:
            choices = room.puzzle.get("wrong_responses") or []
            if choices:
                wr = random.choice(choices)
        print(wr or message)


# Game loop

def run_game():
    # Load world
    try:
        world = load_world()  # reads data/world.json
    except FileNotFoundError:
        print("Could not find data/world.json. Make sure the file exists.")
        return
    except Exception as e:
        print("Failed to load world:", e)
        return

    rooms = build_rooms(world)
    start_room = world.get("start_room", "")
    if not start_room or start_room not in rooms:
        print("Invalid or missing start room in world.json.")
        return

    # Create player
    player = Player(start_room)

    print("Welcome to HAUNTED HOUSE: Study Break")
    print("Type 'help' for commands. Good luck.")
    describe_current_room(player, rooms)

    # Command loop
    while True:
        cmd = input("\n> ").strip().lower()
        if not cmd:
            print("Please type a command. Type 'help' if stuck.")
            continue

        parts = cmd.split()
        verb = parts[0]
        args = parts[1:]

        if verb in ("quit", "exit"):
            print("You step back into the silence. Game over.")
            break
        elif verb == "help":
            handle_help()
        elif verb == "look":
            handle_look(player, rooms)
        elif verb == "inventory" or verb == "inv":
            handle_inventory(player)
        elif verb == "go":
            handle_go(player, rooms, args)
        elif verb == "take":
            handle_take(player, rooms, args)
        elif verb == "inspect":
            handle_inspect(player, rooms, world["items"], args)
        elif verb == "solve":
            result = handle_solve(player, rooms)
            if result == "WIN":
                break
        else:
            print("I don’t understand that. Try 'help'.")

# Allow running this file directly for quick testing
if __name__ == "__main__":
    run_game()