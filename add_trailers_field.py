#!/usr/bin/env python3
"""
Script to add 'trailers' field to all games in JSON files
This adds an empty array for the trailers field to games that don't have it
"""

import json
import sys
import os

def add_trailers_to_json(filename):
    """Add trailers field to all games in a JSON file"""
    print(f"Processing {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Track how many games were updated
        updated_count = 0
        
        # Handle different JSON formats
        if isinstance(data, dict) and 'Games' in data:
            # Format: {"Platform": "...", "Games": [...]}
            games = data['Games']
        elif isinstance(data, dict) and 'games' in data:
            # Format: {"games": [...]}
            games = data['games']
        elif isinstance(data, list):
            # Format: [...]
            games = data
        else:
            print(f"✗ Unknown JSON format in {filename}")
            return False
        
        # Add trailers field to games that don't have it
        for game in games:
            if isinstance(game, dict) and 'trailers' not in game:
                game['trailers'] = []
                updated_count += 1
        
        # Save the updated JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Updated {updated_count} games in {filename}")
        return True
        
    except FileNotFoundError:
        print(f"✗ File not found: {filename}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON in {filename}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error processing {filename}: {e}")
        return False

def main():
    """Main function to process all game JSON files"""
    # List of known platform JSON files
    json_files = [
        'Switch.Games.json',
        'PS3.Games.json',
        'PS4.Games.json',
        'Xbox 360.Games.json'
    ]
    
    success_count = 0
    
    for json_file in json_files:
        if os.path.exists(json_file):
            if add_trailers_to_json(json_file):
                success_count += 1
        else:
            print(f"Skipping {json_file} (not found)")
    
    print(f"\n✓ Successfully processed {success_count} file(s)")
    
    if success_count == 0:
        print("No files were processed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
