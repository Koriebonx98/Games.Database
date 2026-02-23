#!/usr/bin/env python3
"""
Script to scrape PS3 game data from gametdb.com
Extracts all game information from all 108 pages including game ID, name, region, etc.
Stores the data in PS3.Games.json in the standardized format matching PS4.Games.json

This script requires an internet connection to fetch data from gametdb.com.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import time

# Base URL for the PS3 games list
BASE_URL = "https://www.gametdb.com/PS3/List"

# Number of pages to scrape (as per requirements)
TOTAL_PAGES = 108

# Delay between requests to avoid overwhelming the server (in seconds)
REQUEST_DELAY = 0.5

# Known alternate names for popular PS3 games
# This helps make the data more searchable and useful
KNOWN_ALTERNATE_NAMES = {
    "Grand Theft Auto IV": ["GTA IV", "GTA 4"],
    "Grand Theft Auto V": ["GTA V", "GTA 5"],
    "The Last of Us": ["TLOU", "The Last of Us Part 1"],
    "Uncharted: Drake's Fortune": ["Uncharted 1"],
    "Uncharted 2: Among Thieves": ["Uncharted 2"],
    "Uncharted 3: Drake's Deception": ["Uncharted 3"],
    "God of War III": ["GoW III", "GoW 3"],
    "Metal Gear Solid 4: Guns of the Patriots": ["MGS4", "Metal Gear Solid 4"],
    "Call of Duty: Modern Warfare 2": ["CoD MW2", "MW2"],
    "Call of Duty: Black Ops": ["CoD BO", "Black Ops"],
    "Call of Duty: Modern Warfare 3": ["CoD MW3", "MW3"],
    "Call of Duty: Black Ops II": ["CoD BO2", "Black Ops 2"],
    "Red Dead Redemption": ["RDR"],
    "The Elder Scrolls V: Skyrim": ["Skyrim"],
    "Dark Souls": ["Demon's Souls successor"],
    "Assassin's Creed": ["AC"],
    "Assassin's Creed II": ["AC II", "AC 2"],
    "Assassin's Creed: Brotherhood": ["AC Brotherhood"],
    "Assassin's Creed: Revelations": ["AC Revelations"],
    "Assassin's Creed III": ["AC III", "AC 3"],
    "Batman: Arkham Asylum": ["Arkham Asylum"],
    "Batman: Arkham City": ["Arkham City"],
    "LittleBigPlanet": ["LBP"],
    "LittleBigPlanet 2": ["LBP2", "LBP 2"],
    "Resistance: Fall of Man": ["Resistance 1"],
    "Resistance 2": ["R2"],
    "Killzone 2": ["KZ2"],
    "Killzone 3": ["KZ3"],
    "BioShock": ["Bioshock"],
    "BioShock Infinite": ["Bioshock Infinite"],
    "Mass Effect 2": ["ME2"],
    "Mass Effect 3": ["ME3"],
}


def scrape_page(page_number):
    """
    Scrape a single page of PS3 game data
    
    Args:
        page_number (int): The page number to scrape (1-based)
        
    Returns:
        list: List of game dictionaries extracted from the page
    """
    # Construct the URL for the specific page
    if page_number == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?page={page_number}"
    
    print(f"Fetching page {page_number}/{TOTAL_PAGES}: {url}")
    
    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_number}: {e}")
        return []
    
    # Parse the HTML
    soup = BeautifulSoup(response.content, 'lxml')
    
    games_data = []
    
    # GameTDB typically uses table structures for game lists
    # Find the main table containing game data
    # The structure is usually: table with class containing "list" or "games"
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        # Skip the header row and process data rows
        for row in rows[1:]:
            cells = row.find_all('td')
            
            if len(cells) >= 2:
                # Extract game data from cells
                # Typical structure: Game ID, Game Name, Region, Release Date, etc.
                
                # Extract game ID (typically in first column)
                game_id_cell = cells[0]
                game_id = game_id_cell.get_text(strip=True)
                
                # Extract game name (typically in second column)
                game_name_cell = cells[1]
                game_name = game_name_cell.get_text(strip=True)
                
                # Extract region if available (usually third column)
                region = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                
                # Extract min OS version if available
                min_os_version = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                
                # Extract distribution method if available
                distribution_method = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                
                # Extract versions if available
                versions = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                
                # Extract disc description if available
                disc_description = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                
                # Extract type if available
                game_type = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                
                # Only add actual games (skip DLC, demos, system software, etc.)
                if game_type and game_type.lower() != "game":
                    continue
                non_game_name_patterns = [
                    'add-on content pack', 'add-on disc', 'add-on installation disc',
                    'demo disc', 'demo collection', 'demo & trailer',
                    'system software update', 'idu update',
                ]
                if any(pat in game_name.lower() for pat in non_game_name_patterns):
                    continue

                # Only add if we have at least an ID and name
                if game_id and game_name:
                    game_entry = {
                        "title_id": game_id,
                        "game_name": game_name,
                        "region": region,
                        "min_os_version": min_os_version,
                        "distribution_method": distribution_method,
                        "versions": versions,
                        "cartridge_description": disc_description,
                        "type": game_type,
                        "alternate_names": []
                    }
                    games_data.append(game_entry)
    
    print(f"  Extracted {len(games_data)} games from page {page_number}")
    return games_data


def scrape_all_pages():
    """
    Scrape all pages of PS3 game data
    
    Returns:
        list: Combined list of all game dictionaries from all pages
    """
    all_games = []
    
    for page in range(1, TOTAL_PAGES + 1):
        games = scrape_page(page)
        all_games.extend(games)
        
        # Add a delay between requests to be respectful to the server
        if page < TOTAL_PAGES:
            time.sleep(REQUEST_DELAY)
    
    return all_games


def enrich_with_alternate_names(games_list):
    """
    Enrich games with known alternate names
    
    Args:
        games_list (list): List of games in the original format
        
    Returns:
        list: Updated games list with alternate names added
    """
    for game in games_list:
        game_name = game.get('game_name', '')
        
        # If this game has known alternate names and doesn't already have them
        if game_name in KNOWN_ALTERNATE_NAMES:
            # Only add if alternate_names is empty to preserve any existing data
            if not game.get('alternate_names'):
                game['alternate_names'] = KNOWN_ALTERNATE_NAMES[game_name]
    
    return games_list


def convert_to_new_format(games_list):
    """
    Convert the legacy format to the new standardized format
    Matches the format used in PS4.Games.json
    
    Args:
        games_list (list): List of games in legacy format
        
    Returns:
        dict: Games data in new standardized format
    """
    # Transform each game to the new format
    new_games = []
    
    for game in games_list:
        new_game = {
            "Title": game.get('game_name', ''),
            "Region": game.get('region', ''),
            "AlternateNames": game.get('alternate_names', []),
            "Description": "",  # Not available from scraping
            "ReleaseDate": ""   # Not available from scraping
        }
        new_games.append(new_game)
    
    # Create the wrapper structure with Platform key
    output = {
        "Platform": "PS3",
        "Games": new_games
    }
    
    return output


def main():
    """Main function to scrape and save game data"""
    try:
        print(f"Starting to scrape PS3 games from {BASE_URL}")
        print(f"Will scrape {TOTAL_PAGES} pages...\n")
        
        games = scrape_all_pages()
        
        if not games:
            print("\nWarning: No games were extracted!")
            print("This may be due to:")
            print("  - Changes in the website structure")
            print("  - Network connectivity issues")
            print("  - Restricted internet access")
            return 1
        
        # Remove duplicates based on title_id
        unique_games = []
        seen_ids = set()
        for game in games:
            if game['title_id'] not in seen_ids:
                unique_games.append(game)
                seen_ids.add(game['title_id'])
        
        print(f"\nTotal games extracted: {len(games)}")
        print(f"Unique games after deduplication: {len(unique_games)}")
        
        # Enrich with known alternate names
        print("\nEnriching games with known alternate names...")
        unique_games = enrich_with_alternate_names(unique_games)
        
        # Sort alphabetically by game_name (case-insensitive)
        games_list = sorted(unique_games, key=lambda x: (x.get('game_name') or '').lower())
        
        # Convert to new standardized format
        output_data = convert_to_new_format(games_list)
        
        # Save to JSON file in new format
        output_file = "PS3.Games.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully saved {len(output_data['Games'])} games to {output_file}")
        
        # Print a sample of the data in the new format
        print("\nSample of extracted data (first 3 games):")
        for i, game in enumerate(output_data['Games'][:3]):
            print(f"  {game['Title']}")
            print(f"    Region: {game.get('Region', '')}")
            if game.get('AlternateNames'):
                print(f"    Alternate Names: {', '.join(game['AlternateNames'])}")
            if game.get('Description'):
                print(f"    Description: {game['Description'][:50]}...")
            if game.get('ReleaseDate'):
                print(f"    Release Date: {game['ReleaseDate']}")
        
        if len(output_data['Games']) > 3:
            print(f"  ... and {len(output_data['Games']) - 3} more games")
        
        return 0
        
    except Exception as e:
        print(f"\nError during scraping: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("IMPORTANT: This script requires unrestricted internet access.")
        print("If you're seeing connection errors, please run this script")
        print("from an environment with full internet access.")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
