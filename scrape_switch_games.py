#!/usr/bin/env python3
"""
Script to scrape Nintendo Switch game data from switchbrew.org
Extracts game names and title IDs and stores them in Switch.Games.json

This script requires an internet connection to fetch data from switchbrew.org.
If running in a restricted environment, the data may need to be manually compiled.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys

def scrape_from_github_backup():
    """
    Fallback method to scrape data from the GitHub backup repository
    Returns a list of dictionaries containing game names and title IDs
    """
    backup_url = "https://raw.githubusercontent.com/backupbrew/switchbrew/master/Title%20list%20Games.txt"
    
    print(f"Fetching data from GitHub backup: {backup_url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(backup_url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub backup: {e}")
        raise
    
    print(f"Successfully fetched GitHub backup (status code: {response.status_code})")
    
    games_data = []
    lines = response.text.split('\n')
    
    # Parse MediaWiki table format
    # Lines starting with "| 01" contain game data
    for line in lines:
        line = line.strip()
        
        # Skip non-data lines
        if not line.startswith('| 01'):
            continue
        
        # Split by || to get cells
        cells = [cell.strip() for cell in line.split('||')]
        
        if len(cells) >= 2:
            # First cell contains title ID
            title_id_text = cells[0].lstrip('|').strip()
            # Second cell contains game name/description
            game_name_text = cells[1].strip()
            
            # Extract title ID (16-character hex)
            title_id_match = re.search(r'[0-9A-Fa-f]{16}', title_id_text)
            
            if title_id_match and game_name_text:
                # Clean up game name - remove any extra notes in parentheses at the end
                # but preserve Japanese/Chinese characters and main title
                game_name = game_name_text.split('||')[0].strip()
                
                game_entry = {
                    "title_id": title_id_match.group(0).upper(),
                    "game_name": game_name
                }
                games_data.append(game_entry)
    
    print(f"\nExtracted {len(games_data)} games from GitHub backup")
    return games_data

def scrape_switch_games():
    """
    Scrape Nintendo Switch game data from switchbrew.org
    Returns a list of dictionaries containing game names and title IDs
    """
    url = "https://switchbrew.org/w/index.php?title=Title_list/Games&mobileaction=toggle_view_desktop"
    
    print(f"Fetching data from {url}...")
    
    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        print("\nNote: This script requires internet access to switchbrew.org.")
        print("Attempting to use GitHub backup as fallback...")
        
        try:
            return scrape_from_github_backup()
        except Exception as backup_error:
            print(f"GitHub backup also failed: {backup_error}")
            print("\nIf you're in a restricted environment, you may need to:")
            print("  1. Run this script from a machine with unrestricted internet access")
            print("  2. Manually compile the data from the website")
            print("  3. Use an alternative data source")
            raise
    
    print(f"Successfully fetched page (status code: {response.status_code})")
    print(f"Page size: {len(response.content)} bytes")
    
    # Parse the HTML
    soup = BeautifulSoup(response.content, 'lxml')
    
    games_data = []
    
    # Find all tables with class "wikitable" or "sortable"
    # The switchbrew page uses these classes for data tables
    tables = soup.find_all('table', {'class': ['wikitable', 'sortable']})
    
    if not tables:
        # Fallback: try finding any table
        tables = soup.find_all('table')
    
    print(f"Found {len(tables)} tables on the page")
    
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        
        # Get header row to understand column structure
        header_row = rows[0] if rows else None
        headers = []
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            print(f"\nTable {table_idx + 1} headers: {headers}")
            print(f"Table {table_idx + 1} has {len(rows)} rows")
        
        # Process data rows (skip header)
        row_count = 0
        for row_idx, row in enumerate(rows[1:], start=1):
            cells = row.find_all('td')
            
            if len(cells) >= 2:
                # Extract text from cells
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # The first cell typically contains the Title ID
                # The second cell contains the game name/description
                title_id_text = cell_texts[0] if len(cell_texts) > 0 else ""
                game_name_text = cell_texts[1] if len(cell_texts) > 1 else ""
                
                # Title IDs are 16-character hexadecimal values
                title_id_match = re.search(r'[0-9A-Fa-f]{16}', title_id_text)
                
                if title_id_match and game_name_text:
                    game_entry = {
                        "title_id": title_id_match.group(0).upper(),
                        "game_name": game_name_text
                    }
                    games_data.append(game_entry)
                    row_count += 1
        
        print(f"  Extracted {row_count} games from table {table_idx + 1}")
    
    print(f"\nExtracted {len(games_data)} games total")
    
    # If we got very few results, try the GitHub backup as fallback
    if len(games_data) < 100:
        print("\nWarning: Extracted fewer than 100 games from main site.")
        print("This may indicate incomplete data. Trying GitHub backup as fallback...")
        try:
            backup_data = scrape_from_github_backup()
            if len(backup_data) > len(games_data):
                print(f"GitHub backup has more data ({len(backup_data)} vs {len(games_data)}), using backup.")
                return backup_data
        except Exception as e:
            print(f"Could not fetch from GitHub backup: {e}")
            print("Continuing with data from main site...")
    
    return games_data

def main():
    """Main function to scrape and save game data"""
    try:
        games = scrape_switch_games()
        
        if not games:
            print("\nWarning: No games were extracted!")
            print("This may be due to:")
            print("  - Changes in the website structure")
            print("  - Network connectivity issues")
            print("  - Restricted internet access")
            return 1
        
        # Group games by title_id and collect all regional names
        # Use a dict to track games by title_id
        games_by_id = {}
        for game in games:
            title_id = game['title_id']
            game_name = game['game_name']
            
            if title_id not in games_by_id:
                games_by_id[title_id] = {
                    'title_id': title_id,
                    'game_name': game_name,
                    'regions': [game_name]
                }
            else:
                # Add this name to regions if it's not already there
                if game_name not in games_by_id[title_id]['regions']:
                    games_by_id[title_id]['regions'].append(game_name)
        
        # Convert to list and sort by title_id for consistency
        games_list = sorted(games_by_id.values(), key=lambda x: x['title_id'])
        
        # For entries with only one region, remove the regions array to keep it clean
        for game in games_list:
            if len(game['regions']) == 1:
                del game['regions']
        
        duplicates_merged = len(games) - len(games_list)
        if duplicates_merged > 0:
            print(f"\nMerged {duplicates_merged} duplicate entries into regional variations")
        
        # Count how many games have multiple regions
        multi_region_count = sum(1 for game in games_list if 'regions' in game)
        if multi_region_count > 0:
            print(f"Found {multi_region_count} games with multiple regional variations")
        
        # Save to JSON file
        output_file = "Switch.Games.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(games_list, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully saved {len(games_list)} unique games to {output_file}")
        
        # Print a sample of the data
        print("\nSample of extracted data (first 5 games):")
        for game in games_list[:5]:
            if 'regions' in game:
                print(f"  {game['title_id']}: {game['game_name']} ({len(game['regions'])} regions)")
            else:
                print(f"  {game['title_id']}: {game['game_name']}")
        
        if len(games_list) > 5:
            print(f"  ... and {len(games_list) - 5} more games")
        
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
