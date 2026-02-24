#!/usr/bin/env python3
"""
Compile PC.Games.json by merging individual game info.json files from
Data/PC/Games/ into the existing PC.Games.json.

Each game must have its own directory under Data/PC/Games/<Title>/ containing
an info.json file with the game's metadata.

This script MERGES curated games into the existing PC.Games.json (which may
contain a large Steam catalogue) rather than replacing it entirely.
For each game found in Data/PC/Games/:
  - If a matching title already exists in PC.Games.json the curated metadata
    is overlaid onto that entry (preserving Steam catalogue fields).
  - If no match is found the game is appended as a custom entry.

Usage:
    python compile_pc_games.py

This script is also run automatically via GitHub Actions whenever files in
Data/PC/Games/ are added, modified, or removed.
"""

import json
import os
from pathlib import Path


GAMES_DIR   = Path("Data/PC/Games")
OUTPUT_FILE = Path("PC.Games.json")


def _get_title(game):
    return game.get("Title") or game.get("title") or ""


def compile_games():
    """Read all game info.json files and merge into PC.Games.json."""
    if not GAMES_DIR.is_dir():
        print(f"Error: {GAMES_DIR} directory not found")
        return False

    # ── 1. Load curated game entries ─────────────────────────────────────────
    curated = []
    errors  = 0

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

            if "Title" not in game_data:
                print(
                    f"Warning: {info_file} has no 'Title' field; "
                    f"using directory name '{game_dir.name}'"
                )
                game_data["Title"] = game_dir.name

            curated.append(game_data)
            print(f"  Loaded curated: {game_data.get('Title', game_dir.name)}")

        except json.JSONDecodeError as e:
            print(f"Error: Could not parse {info_file}: {e}")
            errors += 1
        except OSError as e:
            print(f"Error: Could not read {info_file}: {e}")
            errors += 1

    if errors:
        print(f"\n{errors} error(s) encountered. PC.Games.json was NOT updated.")
        return False

    # ── 2. Load existing PC.Games.json ────────────────────────────────────────
    existing_games = []
    top_meta       = {}
    top_key        = "Games"
    is_bare_list   = False

    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

            if isinstance(existing_data, dict):
                top_meta = {
                    k: v for k, v in existing_data.items()
                    if k not in ("Games", "games")
                }
                if "Games" in existing_data:
                    existing_games = existing_data["Games"]
                    top_key        = "Games"
                elif "games" in existing_data:
                    existing_games = existing_data["games"]
                    top_key        = "games"
            elif isinstance(existing_data, list):
                existing_games = existing_data
                is_bare_list   = True

            print(
                f"  Loaded {len(existing_games)} existing game(s) from {OUTPUT_FILE}"
            )
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not read existing {OUTPUT_FILE}: {e}")
            existing_games = []

    if not curated:
        print(f"\nNo curated games found in {GAMES_DIR}. {OUTPUT_FILE} unchanged.")
        return True

    # ── 3. Build a lookup of existing games by normalised title ───────────────
    games_by_title = {}
    for idx, g in enumerate(existing_games):
        t = _get_title(g).lower()
        if t:
            games_by_title[t] = idx

    # ── 4. Merge curated games into the existing list ─────────────────────────
    for cg in curated:
        name_lower = _get_title(cg).lower()
        if name_lower in games_by_title:
            idx  = games_by_title[name_lower]
            base = dict(existing_games[idx])
            # Preserve the canonical title from the existing entry before merging
            canonical_title = base.get("Title")
            base.update(cg)
            if canonical_title:
                base["Title"] = canonical_title
            existing_games[idx] = base
            print(f"  Updated: {cg.get('Title', name_lower)}")
        else:
            existing_games.append(cg)
            games_by_title[name_lower] = len(existing_games) - 1
            print(f"  Added:   {cg.get('Title', name_lower)}")

    # ── 5. Write merged output ────────────────────────────────────────────────
    if is_bare_list:
        output = existing_games
    else:
        output = {**top_meta, top_key: existing_games}

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\nWrote {len(existing_games)} game(s) to {OUTPUT_FILE}")
    except OSError as e:
        print(f"Error: Could not write {OUTPUT_FILE}: {e}")
        return False

    return True


if __name__ == "__main__":
    print(
        f"Merging curated games from {GAMES_DIR}/*/info.json "
        f"into {OUTPUT_FILE} ...\n"
    )
    success = compile_games()
    if not success:
        raise SystemExit(1)
