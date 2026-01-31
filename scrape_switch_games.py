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
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        print("\nNote: This script requires internet access to switchbrew.org.")
        print("If you're in a restricted environment, you may need to:")
        print("  1. Run this script from a machine with unrestricted internet access")
        print("  2. Manually compile the data from the website")
        print("  3. Use an alternative data source")
        raise
    
    print(f"Successfully fetched page (status code: {response.status_code})")
    
    # Parse the HTML
    soup = BeautifulSoup(response.content, 'lxml')
    
    games_data = []
    
    # Find the table containing game data
    # The switchbrew page typically has tables with class "wikitable"
    tables = soup.find_all('table', {'class': 'wikitable'})
    
    print(f"Found {len(tables)} tables on the page")
    
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        
        # Get header row to understand column structure
        header_row = rows[0] if rows else None
        headers = []
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            print(f"\nTable {table_idx + 1} headers: {headers}")
        
        # Process data rows
        for row_idx, row in enumerate(rows[1:], start=1):
            cells = row.find_all('td')
            
            if len(cells) >= 2:
                # Extract text from cells
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # The first cell typically contains the Title ID
                # The second or later cell contains the game name
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
    
    print(f"\nExtracted {len(games_data)} games total")
    
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
        
        # Save to JSON file
        output_file = "Switch.Games.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(games, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully saved {len(games)} games to {output_file}")
        
        # Print a sample of the data
        print("\nSample of extracted data (first 5 games):")
        for game in games[:5]:
            print(f"  {game['title_id']}: {game['game_name']}")
        
        if len(games) > 5:
            print(f"  ... and {len(games) - 5} more games")
        
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
