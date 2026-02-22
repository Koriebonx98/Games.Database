#!/usr/bin/env python3
"""
Compile PC.Games.json from individual game info.json files in Data/PC/Games/.

Each game must have its own directory under Data/PC/Games/<Title>/ containing
an info.json file with the game's metadata.

Usage:
    python compile_pc_games.py

This script is also run automatically via GitHub Actions whenever files in
Data/PC/Games/ are added, modified, or removed.
"""

import json
import os
from pathlib import Path


GAMES_DIR = Path("Data/PC/Games")
OUTPUT_FILE = Path("PC.Games.json")


def compile_games():
    """Read all game info.json files and write PC.Games.json."""
    if not GAMES_DIR.is_dir():
        print(f"Error: {GAMES_DIR} directory not found")
        return False

    games = []
    errors = 0

    for game_dir in sorted(GAMES_DIR.iterdir()):
        if not game_dir.is_dir():
            continue

        info_file = game_dir / "info.json"
        if not info_file.exists():
            print(f"Warning: {game_dir.name}/ has no info.json, skipping")
            continue

        try:
            with open(info_file, "r", encoding="utf-8") as f:
                game_data = json.load(f)

            if not isinstance(game_data, dict):
                print(f"Warning: {info_file} does not contain a JSON object, skipping")
                continue

            # Ensure the Title field matches the directory name if missing
            if "Title" not in game_data:
                print(f"Warning: {info_file} has no 'Title' field; using directory name '{game_dir.name}'")
                game_data["Title"] = game_dir.name

            games.append(game_data)
            print(f"  Loaded: {game_data.get('Title', game_dir.name)}")

        except json.JSONDecodeError as e:
            print(f"Error: Could not parse {info_file}: {e}")
            errors += 1
        except OSError as e:
            print(f"Error: Could not read {info_file}: {e}")
            errors += 1

    if errors:
        print(f"\n{errors} error(s) encountered. PC.Games.json was NOT updated.")
        return False

    output = {"Games": games}

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\nWrote {len(games)} game(s) to {OUTPUT_FILE}")
    except OSError as e:
        print(f"Error: Could not write {OUTPUT_FILE}: {e}")
        return False

    return True


if __name__ == "__main__":
    print(f"Compiling {OUTPUT_FILE} from {GAMES_DIR}/*/info.json ...\n")
    success = compile_games()
    if not success:
        raise SystemExit(1)
