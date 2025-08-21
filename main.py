"""
Entry point for the Escape Room game.
Uses argparse to allow optional command-line arguments.
"""

from argparse import ArgumentParser
from game import run_game

def main():
    parser = ArgumentParser(
        description="Haunted House: Study Break -- Escape Room Game"
    )
    parser.add_argument(
        "-w", "--world",
        default="data/world.json",
        help="Path to the world JSON file (default: data/world.json)"
    )
    args = parser.parse_args()

    # Pass chosen world file to run_game
    run_game(world_file=args.world)

if __name__ == "__main__":
    main()