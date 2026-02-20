#!/usr/bin/env python3
"""
Script to populate cover images for Xbox 360 games.
Reads Xbox 360.Games.json, creates a directory for each game under
Data/Microsoft - Xbox 360/Games/<TitleID>/, writes a Name.txt file,
and updates the 'image' field in the JSON.

Primary source: Xbox CDN cover art constructed directly from the title ID —
no API key required.

Optional enhancement: If the STEAMGRIDDB_API_KEY environment variable is set,
SteamGridDB is queried first and its result takes priority over the Xbox CDN
URL for any game where a match is found.

A log file (scrape_xbox360_games.log) is written alongside console output
so every step is recorded for later inspection.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Logging setup — writes to both stdout and a log file
# ---------------------------------------------------------------------------
LOG_FILE = "scrape_xbox360_games.log"

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

# SteamGridDB API configuration — optional enhancement.
# Set the STEAMGRIDDB_API_KEY environment variable to enable SteamGridDB lookups.
STEAMGRIDDB_API_KEY = os.environ.get("STEAMGRIDDB_API_KEY", "")
STEAMGRIDDB_BASE_URL = "https://www.steamgriddb.com/api/v2"

# Xbox CDN cover art URL template.
# Cover images for officially published Xbox 360 titles are available at this URL
# using the game's 8-character hexadecimal title ID (lowercase).
XBOX_CDN_COVER_URL = (
    "https://download.xbox.com/content/images/"
    "66acd000-77fe-1000-9115-d802{titleid}/1033/boxartlg.jpg"
)

# Delay between SteamGridDB API requests to respect rate limits (seconds)
REQUEST_DELAY = 0.3

# Input / output files
XBOX360_JSON_FILE = "Xbox 360.Games.json"

# Directory where per-game folders are created
GAMES_BASE_DIR = Path("Data/Microsoft - Xbox 360/Games")


def xbox_cdn_cover(title_id):
    """
    Return the Xbox CDN cover art URL for the given title ID.

    The URL is constructed directly from the title ID — no network request
    is made here.  The resulting URL points to official Microsoft cover art
    for the game and works for all commercially released Xbox 360 titles.
    """
    return XBOX_CDN_COVER_URL.format(titleid=title_id.lower())


def steamgriddb_headers():
    """Return the authentication headers required by SteamGridDB."""
    return {"Authorization": f"Bearer {STEAMGRIDDB_API_KEY}"}


def search_game_steamgriddb(game_title):
    """
    Search SteamGridDB for a game by title.

    Returns the first matching game's ID, or None if nothing is found.
    Only called when STEAMGRIDDB_API_KEY is set.
    """
    url = f"{STEAMGRIDDB_BASE_URL}/search/autocomplete/{requests.utils.quote(game_title)}"
    try:
        response = requests.get(url, headers=steamgriddb_headers(), timeout=15)
        response.raise_for_status()
        data = response.json()
        if data.get("success") and data.get("data"):
            return data["data"][0]["id"]
    except requests.exceptions.RequestException as exc:
        log.warning("SteamGridDB search failed for '%s': %s", game_title, exc)
    except (KeyError, ValueError) as exc:
        log.warning("Unexpected SteamGridDB response for '%s': %s", game_title, exc)
    return None


def get_cover_url_steamgriddb(game_id):
    """
    Fetch the best available cover (grid image) for a SteamGridDB game ID.

    Tries portrait covers (600x900) first, then falls back to any available grid.
    Returns a URL string, or an empty string if nothing is found.
    Only called when STEAMGRIDDB_API_KEY is set.
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
            log.warning("SteamGridDB grid request failed (game_id=%s): %s", game_id, exc)
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
        log.warning("SteamGridDB fallback grid request failed (game_id=%s): %s", game_id, exc)
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
        log.warning("Could not create directory for %s: %s", title_id, exc)


def main():
    """Main entry point."""
    log.info("=== Xbox 360 cover scraper started ===")
    log.info("Log file: %s", Path(LOG_FILE).resolve())

    use_steamgriddb = bool(STEAMGRIDDB_API_KEY)
    if use_steamgriddb:
        log.info("STEAMGRIDDB_API_KEY is set — SteamGridDB will be used as primary source.")
    else:
        log.info("STEAMGRIDDB_API_KEY not set — using Xbox CDN cover URLs (no API key required).")

    # Load the Xbox 360 games JSON
    json_path = Path(XBOX360_JSON_FILE)
    if not json_path.exists():
        log.error("%s not found.", XBOX360_JSON_FILE)
        return 1

    with open(json_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    games = data.get("games", [])
    if not games:
        log.error("No games found in JSON.")
        return 1

    total = len(games)
    log.info("Loaded %d Xbox 360 games from %s", total, XBOX360_JSON_FILE)
    log.info("Creating directories under %s and updating covers...", GAMES_BASE_DIR)

    updated = 0
    skipped = 0
    no_match = 0

    for idx, game in enumerate(games, start=1):
        title_id = game.get("titleid", "").strip()
        game_title = game.get("title", "").strip()

        if not title_id or not game_title:
            log.warning("[%d/%d] Skipping entry with missing titleid or title", idx, total)
            skipped += 1
            continue

        # Already has a cover — keep it
        existing_image = game.get("image", "")
        if existing_image:
            log.debug("[%d/%d] %s — image already set, skipping", idx, total, game_title)
            create_game_directory(title_id, game_title)
            skipped += 1
            continue

        log.info("[%d/%d] Processing: %s (%s)", idx, total, game_title, title_id)

        # Create the per-game directory + Name.txt
        create_game_directory(title_id, game_title)

        cover_url = ""

        if use_steamgriddb:
            # Try SteamGridDB first when API key is available
            sgdb_id = search_game_steamgriddb(game_title)
            time.sleep(REQUEST_DELAY)

            if sgdb_id is not None:
                log.info("  -> SteamGridDB game_id=%s, fetching cover...", sgdb_id)
                cover_url = get_cover_url_steamgriddb(sgdb_id)
                time.sleep(REQUEST_DELAY)

                if cover_url:
                    log.info("  -> SteamGridDB cover found: %s", cover_url)
                    updated += 1
                else:
                    log.info("  -> No SteamGridDB cover found (game_id=%s), falling back to Xbox CDN", sgdb_id)
            else:
                log.info("  -> No SteamGridDB match for '%s', falling back to Xbox CDN", game_title)

        if not cover_url:
            # Use Xbox CDN cover URL (works for all officially released Xbox 360 titles)
            cover_url = xbox_cdn_cover(title_id)
            log.info("  -> Xbox CDN cover URL: %s", cover_url)
            updated += 1

        game["image"] = cover_url

    # Save the updated JSON
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

    log.info("=== Scrape complete ===")
    log.info("  Total games    : %d", total)
    log.info("  Covers updated : %d", updated)
    log.info("  Skipped        : %d", skipped)
    log.info("  Saved to       : %s", XBOX360_JSON_FILE)
    log.info("  Log written    : %s", LOG_FILE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
