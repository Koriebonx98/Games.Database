#!/usr/bin/env python3
"""
Script to create Name.txt files for each Nintendo Switch game.
Reads Switch.Games.json and creates Name.txt files in data/Nintendo - Switch/Games/{TitleID}/
"""

import json
import os
from pathlib import Path

def create_name_files():
    """Create Name.txt files for all games in Switch.Games.json"""
    
    # Load the Switch games JSON file
    json_file = Path('Switch.Games.json')
    if not json_file.exists():
        print(f"Error: {json_file} not found!")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    print(f"Found {len(games)} games in Switch.Games.json")
    
    # Base directory for Switch games
    base_dir = Path('Data/Nintendo - Switch/Games')
    
    # Create Name.txt file for each game
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for game in games:
        title_id = game.get('title_id')
        game_name = game.get('game_name')
        
        if not title_id or not game_name:
            print(f"Warning: Skipping game with missing title_id or game_name: {game}")
            skipped_count += 1
            continue
        
        # Create the directory path
        game_dir = base_dir / title_id
        
        # Create directory if it doesn't exist
        try:
            game_dir.mkdir(parents=True, exist_ok=True)
            
            # Create Name.txt file
            name_file = game_dir / 'Name.txt'
            with open(name_file, 'w', encoding='utf-8') as f:
                f.write(game_name)
            
            created_count += 1
            
            # Print progress every 100 games
            if created_count % 100 == 0:
                print(f"Progress: {created_count}/{len(games)} games processed...")
                
        except Exception as e:
            print(f"Error creating Name.txt for {title_id} ({game_name}): {e}")
            error_count += 1
    
    print("\n" + "="*60)
    print("Summary:")
    print(f"  Total games: {len(games)}")
    print(f"  Name.txt files created: {created_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    print("="*60)

if __name__ == '__main__':
    create_name_files()
