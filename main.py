"""
Entry point for the Escape Room game.
This script sets up command-line argument parsing so players can optionally
choose which game world file to load. By default, it uses "data/world.json".
"""

from argparse import ArgumentParser
from game import run_game

def main():
    """
    Set up and launch the Escape Room game.

    This function handles command-line arguments using argparse. It lets the
    user optionally give a path to a JSON file that defines the game world.
    Once arguments are parsed, it calls run_game to start the game.

    Parameters:
        None

    Returns:
        None

    Side Effects:
        Reads command-line arguments and passes the chosen world file to
        run_game, which launches the game.
    """
    parser = ArgumentParser(
        description="Haunted House: Study Break --- Escape Room Game"
    )
    # Allow players to load a custom world file instead of the default one
    parser.add_argument(
        "-w", "--world",
        default="data/world.json",
        help="Path to the world JSON file (default: data/world.json)"
    )
    args = parser.parse_args()

    # Pass chosen world file to run_game
    run_game(world_file=args.world)

# Only start the game if this file is run directly, not when imported
if __name__ == "__main__":
    main()