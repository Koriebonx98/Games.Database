#!/usr/bin/env python3
"""
Script to scrape PS3 game data from gametdb.com
Extracts all game information from all 108 pages including game ID, name, region, etc.
Stores the data in ps3.games.json

This script requires an internet connection to fetch data from gametdb.com.
If the main site is unavailable, it falls back to the GitHub backup (niemasd/GameDB-PS3).
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import time

# Base URL for the PS3 games list
BASE_URL = "https://www.gametdb.com/PS3/List"

# Backup/fallback data source
BACKUP_DATA_URL = "https://github.com/niemasd/GameDB-PS3/releases/latest/download/PS3.data.json"
BACKUP_TITLES_URL = "https://github.com/niemasd/GameDB-PS3/releases/latest/download/PS3.titles.json"

# Expected total games from GameTDB (includes regional variants, updates, DLC)
EXPECTED_GAMETDB_TOTAL = 10766

# Number of pages to scrape (as per requirements)
TOTAL_PAGES = 108

# Delay between requests to avoid overwhelming the server (in seconds)
REQUEST_DELAY = 0.5


def scrape_from_github_backup():
    """
    Fallback method to scrape data from the GitHub backup repository
    Uses niemasd/GameDB-PS3 which provides comprehensive PS3 game data
    Returns a list of dictionaries containing game data with all fields
    """
    print(f"Fetching data from GitHub backup: {BACKUP_DATA_URL}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(BACKUP_DATA_URL, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub backup: {e}")
        raise
    
    print(f"Successfully fetched GitHub backup (status code: {response.status_code})")
    
    # Parse the JSON data
    # Format: { "SERIAL": { "title": "Game Name", "region": "NTSC-U", "language": [...] }, ... }
    backup_data = response.json()
    
    games_data = []
    
    for serial, game_info in backup_data.items():
        # Extract game information
        title = game_info.get('title', '')
        region_code = game_info.get('region', '')
        languages = game_info.get('language', [])
        
        # Map region codes to readable format
        region_map = {
            'NTSC-U': 'USA',
            'NTSC-J': 'JPN',
            'PAL': 'EUR',
            'NTSC-K': 'KOR',
            'NTSC-C': 'CHN',
        }
        region = region_map.get(region_code, region_code)
        
        if serial and title:
            game_entry = {
                "title_id": serial,
                "game_name": title,
                "region": region,
                "min_os_version": "",
                "distribution_method": "",  # Not available in backup data
                "versions": "",
                "cartridge_description": "",  # Not available in backup data
                "type": "Game",
                "alternate_names": []
            }
            games_data.append(game_entry)
    
    print(f"\nExtracted {len(games_data)} games from GitHub backup")
    return games_data


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
    
    # First, try to access the main site to see if it's available
    print("Checking if main site (gametdb.com) is accessible...")
    try:
        test_response = requests.get(BASE_URL, timeout=10)
        test_response.raise_for_status()
        print("Main site is accessible. Proceeding with scraping...\n")
        site_accessible = True
    except requests.exceptions.RequestException as e:
        print(f"Main site is not accessible: {e}")
        print("Will use GitHub backup instead.\n")
        site_accessible = False
    
    if not site_accessible:
        # Use backup data source
        return scrape_from_github_backup()
    
    # If main site is accessible, scrape all pages
    for page in range(1, TOTAL_PAGES + 1):
        games = scrape_page(page)
        all_games.extend(games)
        
        # Add a delay between requests to be respectful to the server
        if page < TOTAL_PAGES:
            time.sleep(REQUEST_DELAY)
    
    return all_games


def main():
    """Main function to scrape and save game data"""
    try:
        print(f"Starting to scrape PS3 games from {BASE_URL}")
        print(f"Will scrape {TOTAL_PAGES} pages (or use backup if main site unavailable)...\n")
        
        games = scrape_all_pages()
        
        if not games:
            print("\nWarning: No games were extracted!")
            print("This may be due to:")
            print("  - Changes in the website structure")
            print("  - Network connectivity issues")
            print("  - Restricted internet access")
            print("\nTrying GitHub backup as last resort...")
            try:
                games = scrape_from_github_backup()
            except Exception as backup_error:
                print(f"GitHub backup also failed: {backup_error}")
                return 1
        
        if not games:
            print("\nFailed to extract any games from any source.")
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
        
        # Sort alphabetically by game_name (case-insensitive)
        games_list = sorted(unique_games, key=lambda x: (x.get('game_name') or '').lower())
        
        # Save to JSON file with all fields including alternate_names
        output_file = "ps3.games.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(games_list, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully saved {len(games_list)} games to {output_file}")
        
        # Print a sample of the data
        print("\nSample of extracted data (first 3 games):")
        for game in games_list[:3]:
            print(f"  {game['title_id']}: {game['game_name']}")
            print(f"    Region: {game.get('region', '')}")
            print(f"    Min OS: {game.get('min_os_version', '')}")
            print(f"    Distribution: {game.get('distribution_method', '')}")
            print(f"    Type: {game.get('type', '')}")
            if game.get('alternate_names'):
                print(f"    Alternate Names: {', '.join(game['alternate_names'])}")
        
        if len(games_list) > 3:
            print(f"  ... and {len(games_list) - 3} more games")
        
        # Note about the count
        if len(games_list) < EXPECTED_GAMETDB_TOTAL:
            print(f"\nNote: Extracted {len(games_list)} games. If you expected more (e.g., {EXPECTED_GAMETDB_TOTAL}),")
            print("this may be because:")
            print("  - The backup source (niemasd/GameDB-PS3) contains unique game serials only")
            print("  - GameTDB counts regional variants and updates separately")
            print("  - The main site (gametdb.com) was not accessible from this environment")
        
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
