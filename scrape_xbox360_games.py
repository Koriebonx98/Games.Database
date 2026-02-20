#!/usr/bin/env python3
"""
Script to scrape cover images for Xbox 360 games using the SteamGridDB API.
Reads Xbox 360.Games.json, creates a directory for each game under
Data/Microsoft - Xbox 360/Games/<TitleID>/, writes a Name.txt file,
and updates the 'image' field in the JSON with the best cover URL found.

Requires internet access to reach api.steamgriddb.com.
"""

import json
import os
import sys
import time
from pathlib import Path

import requests

# SteamGridDB API configuration
# Can be overridden by setting the STEAMGRIDDB_API_KEY environment variable.
STEAMGRIDDB_API_KEY = os.environ.get("STEAMGRIDDB_API_KEY", "2520d628f08a9975c1f34f9a5349ff88")
STEAMGRIDDB_BASE_URL = "https://www.steamgriddb.com/api/v2"

# Delay between API requests to respect rate limits (seconds)
REQUEST_DELAY = 0.3

# Input / output files
XBOX360_JSON_FILE = "Xbox 360.Games.json"

# Directory where per-game folders are created
GAMES_BASE_DIR = Path("Data/Microsoft - Xbox 360/Games")


def steamgriddb_headers():
    """Return the authentication headers required by SteamGridDB."""
    return {"Authorization": f"Bearer {STEAMGRIDDB_API_KEY}"}


def search_game(game_title):
    """
    Search SteamGridDB for a game by title.

    Returns the first matching game's ID, or None if nothing is found.
    """
    url = f"{STEAMGRIDDB_BASE_URL}/search/autocomplete/{requests.utils.quote(game_title)}"
    try:
        response = requests.get(url, headers=steamgriddb_headers(), timeout=15)
        response.raise_for_status()
        data = response.json()
        if data.get("success") and data.get("data"):
            return data["data"][0]["id"]
    except requests.exceptions.RequestException as exc:
        print(f"    Warning: search request failed for '{game_title}': {exc}")
    except (KeyError, ValueError) as exc:
        print(f"    Warning: unexpected search response for '{game_title}': {exc}")
    return None


def get_cover_url(game_id):
    """
    Fetch the best available cover (grid image) for a SteamGridDB game ID.

    Tries portrait covers (600x900) first, then falls back to any available grid.
    Returns a URL string, or an empty string if nothing is found.
    """
    # Prefer portrait/box-art style grids
    for dimensions in ("600x900", "342x482", "660x930"):
        url = f"{STEAMGRIDDB_BASE_URL}/grids/game/{game_id}"
        params = {"dimensions": dimensions, "limit": 1}
        try:
            response = requests.get(
                url, headers=steamgriddb_headers(), params=params, timeout=15
            )
            response.raise_for_status()
            data = response.json()
            if data.get("success") and data.get("data"):
                return data["data"][0]["url"]
        except requests.exceptions.RequestException as exc:
            print(f"    Warning: grid request failed (game_id={game_id}): {exc}")
            break
        except (KeyError, ValueError):
            pass

    # Final fallback: any grid without dimension filter
    url = f"{STEAMGRIDDB_BASE_URL}/grids/game/{game_id}"
    try:
        response = requests.get(
            url, headers=steamgriddb_headers(), params={"limit": 1}, timeout=15
        )
        response.raise_for_status()
        data = response.json()
        if data.get("success") and data.get("data"):
            return data["data"][0]["url"]
    except requests.exceptions.RequestException as exc:
        print(f"    Warning: fallback grid request failed (game_id={game_id}): {exc}")
    except (KeyError, ValueError):
        pass

    return ""


def create_game_directory(title_id, game_title):
    """
    Create the Data/Microsoft - Xbox 360/Games/<TitleID>/ directory and
    write a Name.txt file containing the game title.
    """
    game_dir = GAMES_BASE_DIR / title_id
    try:
        game_dir.mkdir(parents=True, exist_ok=True)
        name_file = game_dir / "Name.txt"
        with open(name_file, "w", encoding="utf-8") as fh:
            fh.write(game_title)
    except OSError as exc:
        print(f"    Warning: could not create directory for {title_id}: {exc}")


def main():
    """Main entry point."""
    # Load the Xbox 360 games JSON
    json_path = Path(XBOX360_JSON_FILE)
    if not json_path.exists():
        print(f"Error: {XBOX360_JSON_FILE} not found.")
        return 1

    with open(json_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    games = data.get("games", [])
    if not games:
        print("Error: no games found in JSON.")
        return 1

    total = len(games)
    print(f"Loaded {total} Xbox 360 games from {XBOX360_JSON_FILE}")
    print(f"Creating directories under {GAMES_BASE_DIR} and fetching covers...\n")

    updated = 0
    skipped = 0

    for idx, game in enumerate(games, start=1):
        title_id = game.get("titleid", "").strip()
        game_title = game.get("title", "").strip()

        if not title_id or not game_title:
            print(f"[{idx}/{total}] Skipping entry with missing titleid or title")
            skipped += 1
            continue

        # Already has a cover — keep it
        existing_image = game.get("image", "")
        if existing_image:
            print(f"[{idx}/{total}] {game_title} — image already set, skipping API call")
            create_game_directory(title_id, game_title)
            skipped += 1
            continue

        print(f"[{idx}/{total}] {game_title} ({title_id})")

        # Create the per-game directory + Name.txt
        create_game_directory(title_id, game_title)

        # Search SteamGridDB for the game
        sgdb_id = search_game(game_title)
        time.sleep(REQUEST_DELAY)

        if sgdb_id is None:
            print(f"    No match found on SteamGridDB")
            game["image"] = ""
            continue

        # Fetch the cover URL
        cover_url = get_cover_url(sgdb_id)
        time.sleep(REQUEST_DELAY)

        game["image"] = cover_url

        if cover_url:
            print(f"    Cover found: {cover_url}")
            updated += 1
        else:
            print(f"    No cover image available (game_id={sgdb_id})")

    # Save the updated JSON
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

    print(f"\nDone.")
    print(f"  Total games : {total}")
    print(f"  Covers added: {updated}")
    print(f"  Skipped     : {skipped}")
    print(f"  Saved to    : {XBOX360_JSON_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
