#!/usr/bin/env python3
"""
Script to scrape cover images for Nintendo Switch games using the SteamGridDB API.
Reads Switch.Games.json, creates a directory for each game under
Data/Nintendo - Switch/Games/<TitleID>/, writes a Name.txt file,
and updates the 'image' field in the JSON with the best cover URL found.

Requires internet access to reach api.steamgriddb.com.

A log file (scrape_switch_covers.log) is written alongside console output
so every step is recorded for later inspection.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

# ---------------------------------------------------------------------------
# Logging setup — writes to both stdout and a log file
# ---------------------------------------------------------------------------
LOG_FILE = "scrape_switch_covers.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# SteamGridDB API configuration
# Can be overridden by setting the STEAMGRIDDB_API_KEY environment variable.
STEAMGRIDDB_API_KEY = os.environ.get("STEAMGRIDDB_API_KEY", "2520d628f08a9975c1f34f9a5349ff88")
STEAMGRIDDB_BASE_URL = "https://www.steamgriddb.com/api/v2"

# Delay between API requests to respect rate limits (seconds)
REQUEST_DELAY = 0.3

# Input / output files
SWITCH_JSON_FILE = "Switch.Games.json"

# Directory where per-game folders are created
GAMES_BASE_DIR = Path("Data/Nintendo - Switch/Games")


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
        log.warning("Search request failed for '%s': %s", game_title, exc)
    except (KeyError, ValueError) as exc:
        log.warning("Unexpected search response for '%s': %s", game_title, exc)
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
            log.warning("Grid request failed (game_id=%s): %s", game_id, exc)
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
        log.warning("Fallback grid request failed (game_id=%s): %s", game_id, exc)
    except (KeyError, ValueError):
        pass

    return ""


def create_game_directory(title_id, game_title):
    """
    Create the Data/Nintendo - Switch/Games/<TitleID>/ directory and
    write a Name.txt file containing the game title.
    """
    game_dir = GAMES_BASE_DIR / title_id
    try:
        game_dir.mkdir(parents=True, exist_ok=True)
        name_file = game_dir / "Name.txt"
        with open(name_file, "w", encoding="utf-8") as fh:
            fh.write(game_title)
    except OSError as exc:
        log.warning("Could not create directory for %s: %s", title_id, exc)


def main():
    """Main entry point."""
    log.info("=== Nintendo Switch cover scraper started ===")
    log.info("Log file: %s", Path(LOG_FILE).resolve())

    # Load the Switch games JSON
    json_path = Path(SWITCH_JSON_FILE)
    if not json_path.exists():
        log.error("%s not found.", SWITCH_JSON_FILE)
        return 1

    with open(json_path, "r", encoding="utf-8") as fh:
        games = json.load(fh)

    if not isinstance(games, list) or not games:
        log.error("No games found in JSON.")
        return 1

    total = len(games)
    log.info("Loaded %d Nintendo Switch games from %s", total, SWITCH_JSON_FILE)
    log.info("Creating directories under %s and fetching covers...", GAMES_BASE_DIR)

    updated = 0
    skipped = 0
    no_match = 0

    for idx, game in enumerate(games, start=1):
        title_id = game.get("title_id", "").strip()
        game_title = game.get("game_name", "").strip()

        if not title_id or not game_title:
            log.warning("[%d/%d] Skipping entry with missing title_id or game_name", idx, total)
            skipped += 1
            continue

        # Already has a real cover — keep it
        existing_image = game.get("image", "")
        is_placeholder = urlparse(existing_image).hostname == "via.placeholder.com"
        if existing_image and not is_placeholder:
            log.debug("[%d/%d] %s — image already set, skipping API call", idx, total, game_title)
            create_game_directory(title_id, game_title)
            skipped += 1
            continue

        log.info("[%d/%d] Processing: %s (%s)", idx, total, game_title, title_id)

        # Create the per-game directory + Name.txt
        create_game_directory(title_id, game_title)

        # Search SteamGridDB for the game
        sgdb_id = search_game(game_title)
        time.sleep(REQUEST_DELAY)

        if sgdb_id is None:
            log.info("  -> No match found on SteamGridDB for '%s'", game_title)
            game["image"] = ""
            no_match += 1
            continue

        log.info("  -> SteamGridDB game_id=%s, fetching cover...", sgdb_id)

        # Fetch the cover URL
        cover_url = get_cover_url(sgdb_id)
        time.sleep(REQUEST_DELAY)

        game["image"] = cover_url

        if cover_url:
            log.info("  -> Cover found: %s", cover_url)
            updated += 1
        else:
            log.info("  -> No cover image available (game_id=%s)", sgdb_id)

    # Save the updated JSON
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(games, fh, indent=2, ensure_ascii=False)

    log.info("=== Scrape complete ===")
    log.info("  Total games  : %d", total)
    log.info("  Covers added : %d", updated)
    log.info("  No API match : %d", no_match)
    log.info("  Skipped      : %d", skipped)
    log.info("  Saved to     : %s", SWITCH_JSON_FILE)
    log.info("  Log written  : %s", LOG_FILE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
