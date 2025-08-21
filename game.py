"""
Connects the pieces: loads world.json, builds Room objects, creates Player,
and runs the main command loop (go/take/look/inventory/solve/help/quit).
"""

import time
import random
from world_loader import load_world
from room import Room
from player import Player

GAME_TIME_LIMIT = 5 * 60  # 5 minutes in seconds

def time_left(start_time):
    """Return remaining seconds (can be negative)."""
    return GAME_TIME_LIMIT - (time.monotonic() - start_time)

def format_mmss(seconds):
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"

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
    """Print the current room description with support for revisits and item hints."""
    room = rooms[player.location]
    print("\n=== {} ===".format(room.name.capitalize()))

    if not room.visited:
        # First time seeing this room
        print(room.description)
        room.visited = True
    else:
        # On repeat visits
        print("You’re back in the {}.".format(room.name))

    # Handle items
    if room.items:
        print("You see: " + ", ".join(room.items))
    else:
        # If room originally had items but now empty, remind player
        if room.original_items:
            picked = ", ".join(room.original_items)
            print(f"You already picked up {picked}. Maybe inspect it from your inventory.")
        else:
            print("You see nothing useful here.")

    # Always show exits
    if room.exits:
        print("Exits: " + ", ".join(room.exits.keys()))

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

    # Require flashlight to leave the foyer north
    if current.name == "foyer" and direction == "north" and not player.has_item("flashlight"):
        print("It’s too dark down the hallway. You’re too scared to go without a flashlight.")
        # gentle hint if it’s in the room
        if current.has_item("flashlight"):
            print("Maybe pick up the flashlight first (try: take flashlight).")
        return

    
    if current.has_puzzle() and not current.puzzle.get("solved"):
        if current.name == "hallway" and direction == "east":
            print("The door is still locked. Maybe the keypad code opens it. Try typing 'solve' when you think you know the code.")
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
        # Check if player already has it
        if player.has_item(item):
            print("You already picked up the {}.".format(item))
        else:
            print("There is no '{}' here.".format(item))
        return
    
    room.remove_item(item)
    player.add_item(item)
    print("You picked up the {}.".format(item))
    print("Tip: type 'inspect {}' to examine it more closely.".format(item))

    if item == "flashlight" and player.location == "foyer":
        print("With the flashlight in hand, the hallway looks a lot less terrifying. Try 'go north' now.")

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
    room = rooms[player.location]

    print(f"\n=== {room.name.title()} ===")
    print(room.description)

    # Items handling
    if room.items:
        print("You see: " + ", ".join(room.items))
    else:
        # Check if this room originally had items that are now in player inventory
        if hasattr(room, "original_items"):
            taken_items = [item for item in player.inventory if item in room.original_items]
            if taken_items:
                print("You already picked up " + ", ".join(taken_items) + ".")
            else:
                print("You see nothing useful here.")
        else:
            print("You see nothing useful here.")

    # Exits
    if room.exits:
        print("Exits: " + ", ".join(room.exits))


def handle_help():
    print("Commands you can try:")
    print("  look           - describe the room again")
    print("  go <dir>       - move (north/south/east/west)")
    print("  take <item>    - pick something up")
    print("  inspect <item>   - examine an item in detail")
    print("  inventory      - show what you’re carrying")
    print("  solve          - attempt the current room’s puzzle (if any)")
    print("  time           - show how much time you have left")
    print("  help           - this help")
    print("  quit           - exit the game")


def handle_solve(player, rooms):
    room = rooms[player.location]
    if not room.has_puzzle():
        print("There’s nothing to solve here.")
        return

    # --- Special two-step flow for the Study ---
    if room.name == "study":
        # Stage flag stored on the room's puzzle dict
        lit = room.puzzle.get("lit", False)

        if not lit:
            # Stage 1: it's dark—require the flashlight command
            print("It’s so dark you can barely see. If you have a flashlight, try typing 'flashlight'.")
            answer = input("> ").strip().lower()

            if answer == "flashlight":
                if player.has_item("flashlight"):
                    room.puzzle["lit"] = True
                    print("You click on the flashlight. In the beam, you spot a cracked window letting in a cold draft.")
                    print("You might be able to force it open...")
                else:
                    print("You fumble around, but you don't have a flashlight.")
            else:
                # Any other input at this stage does nothing
                wr = None
                if "wrong_responses" in room.puzzle:
                    choices = room.puzzle.get("wrong_responses") or []
                    if choices:
                        import random
                        wr = random.choice(choices)
                print(wr or "That doesn’t help in the dark.")
            return  # end here; not solved yet

        # Stage 2: room is lit -> proceed to the existing window puzzle
        print(room.puzzle_question())  # from JSON: jammed window prompt
        answer = input("> ").strip()
        success, message = room.try_solve_puzzle(answer)
        if success:
            print(message)
            # Win condition
            print("\nThe window gives way. Cold night air rushes in.")
            print("You crawl out, drop to the grass, and sprint away.")
            print("You escaped the house. Nice work!")
            return "WIN"
        else:
            wr = None
            if room.puzzle and "wrong_responses" in room.puzzle:
                choices = room.puzzle.get("wrong_responses") or []
                if choices:
                    import random
                    wr = random.choice(choices)
            print(wr or message)
        return

    # --- Default behavior for all other rooms (e.g., hallway lock) ---
    print(room.puzzle_question())
    answer = input("> ").strip()
    success, message = room.try_solve_puzzle(answer)
    if success:
        print(message)
        # Hallway convenience hint after unlocking
        if room.name == "hallway":
            print("You hear a metallic click from the east door. It’s unlocked now. You can go east.")
        # If any other room needed special behavior, you could add it here.
    else:
        wr = None
        if room.puzzle and "wrong_responses" in room.puzzle:
            choices = room.puzzle.get("wrong_responses") or []
            if choices:
                import random
                wr = random.choice(choices)
        print(wr or message)


# Game loop

def run_game(world_file="data/world.json"):
    # Load world
    try:
        world = load_world(world_file)  # reads data/world.json
    except FileNotFoundError:
        print(f"Could not find {world_file}. Make sure the file exists.")
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
    
    start_time = time.monotonic()
    print(f"(You feel watched... You have {format_mmss(GAME_TIME_LIMIT)} to escape.)")
    
    print("Welcome to THE HAUNTED HOUSE")
    print("Type 'help' for commands. Good luck.")
    describe_current_room(player, rooms)

    # Command loop
    while True:
        # Check timer each turn
        remaining = time_left(start_time)
        if remaining <= 0:
            print("\nA shadow looms behind you. Claws. Cold breath. Everything goes dark.")
            print("You ran out of time. The house keeps you forever.")
            break
        if remaining <= 60:
            print(f"(Hurry!!! Only {format_mmss(remaining)} left!)")

        prompt = f"\n[{format_mmss(time_left(start_time))}] > "
        cmd = input(prompt).strip().lower()
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
        elif verb == "time" or verb == "status":
            print(f"Time remaining: {format_mmss(time_left(start_time))}")
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
                elapsed = time.monotonic() - start_time
                print(f"\nYou made it out! It took you {format_mmss(int(elapsed))}.")
                # Optional “close call” flair:
                remaining = time_left(start_time)
                if remaining <= 30:
                    print("That was close… you barely made it!")
                break
        else:
            print("I don’t understand that. Try 'help'.")

# Allow running this file directly for quick testing
if __name__ == "__main__":
    run_game()