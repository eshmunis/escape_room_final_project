"""
Core game loop and command handling.
(Temporary stub: Ill wire rooms/items/puzzles in later files.)
"""

def run_game():
    """Run the main game loop (temporary version)."""
    print("Welcome to the Escape Room!")
    print("Type 'help' for commands; 'quit' to exit.")

    while True:
        cmd = input("> ").strip().lower()

        if not cmd:
            print("Please type a command. Type 'help' if stuck.")
            continue

        if cmd in {"quit", "exit"}:
            print("Goodbye!")
            break

        if cmd == "help":
            print("Available right now: help, quit. More coming soon.")
            continue

        # Placeholder for future commands like: go/take/use/solve
        print(f"'{cmd}' isn't implemented yet. Try 'help' or 'quit'.")

if __name__ == "__main__":
    # Optional: lets me run `python game.py` for a quick manual test.
    run_game()