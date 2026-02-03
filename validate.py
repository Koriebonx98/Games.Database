#!/usr/bin/env python3
"""
Validation script for the Games.Database repository.

This script validates:
1. Switch.Games.json file structure and content
2. scrape_switch_games.py Python syntax
3. GitHub workflow configuration

Usage:
    python3 validate.py
"""

import json
import re
import sys
import os


def validate_json_file():
    """Validate Switch.Games.json file."""
    print("=" * 60)
    print("VALIDATING Switch.Games.json")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    try:
        with open('Switch.Games.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✓ JSON syntax is valid")
    except json.JSONDecodeError as e:
        print(f"✗ JSON syntax error: {e}")
        return False
    except FileNotFoundError:
        print("✗ File not found: Switch.Games.json")
        return False
    
    # Check total count
    print(f"✓ Total entries: {len(data)}")
    
    # Check required fields
    missing_fields = []
    for i, entry in enumerate(data):
        if 'title_id' not in entry:
            missing_fields.append(f"Entry {i}: missing 'title_id'")
        if 'game_name' not in entry:
            missing_fields.append(f"Entry {i}: missing 'game_name'")
    
    if missing_fields:
        print(f"✗ Found {len(missing_fields)} entries with missing fields:")
        for msg in missing_fields[:5]:
            print(f"  {msg}")
        errors.append("Missing required fields")
    else:
        print("✓ All entries have required fields (title_id, game_name)")
    
    # Check alphabetical sorting
    game_names = [entry['game_name'] for entry in data]
    sorted_names = sorted(game_names, key=str.lower)
    is_sorted = game_names == sorted_names
    if is_sorted:
        print("✓ Games are sorted alphabetically by game_name")
    else:
        print("✗ Games are NOT sorted alphabetically")
        errors.append("Games not sorted")
    
    # Validate title_id format (16 hex characters)
    title_id_pattern = re.compile(r'^[0-9A-Fa-f]{16}$')
    invalid_title_ids = []
    for entry in data:
        if 'title_id' in entry:
            if not title_id_pattern.match(entry['title_id']):
                invalid_title_ids.append(f"{entry['game_name']}: {entry['title_id']}")
    
    if invalid_title_ids:
        print(f"✗ Found {len(invalid_title_ids)} invalid title_id formats:")
        for msg in invalid_title_ids[:5]:
            print(f"  {msg}")
        errors.append("Invalid title_id formats")
    else:
        print("✓ All title_ids have valid format (16 hex characters)")
    
    # Check for duplicate title_ids
    title_ids = [entry['title_id'] for entry in data]
    duplicate_ids = [tid for tid in set(title_ids) if title_ids.count(tid) > 1]
    if duplicate_ids:
        print(f"✗ Found {len(duplicate_ids)} duplicate title_ids:")
        for tid in duplicate_ids[:5]:
            games = [e['game_name'] for e in data if e['title_id'] == tid]
            print(f"  {tid}: {games}")
        errors.append("Duplicate title_ids found")
    else:
        print("✓ No duplicate title_ids found")
    
    # Check for duplicate game names (warning only, as different regions may have same name)
    game_names_lower = [name.lower() for name in game_names]
    duplicate_names = [name for name in set(game_names_lower) if game_names_lower.count(name) > 1]
    if duplicate_names:
        print(f"ℹ Info: Found {len(duplicate_names)} duplicate game names (likely different regional versions)")
        warnings.append(f"{len(duplicate_names)} duplicate game names")
    else:
        print("✓ No duplicate game names found")
    
    # Check regions field if present
    entries_with_regions = [e for e in data if 'regions' in e]
    print(f"✓ Entries with 'regions' field: {len(entries_with_regions)}")
    if entries_with_regions:
        invalid_regions = []
        for entry in entries_with_regions:
            if not isinstance(entry['regions'], list):
                invalid_regions.append(f"{entry['game_name']}: regions is not a list")
            else:
                for region in entry['regions']:
                    if not isinstance(region, str):
                        invalid_regions.append(f"{entry['game_name']}: region value is not a string")
                        break
        
        if invalid_regions:
            print(f"✗ Found {len(invalid_regions)} invalid regions:")
            for msg in invalid_regions[:5]:
                print(f"  {msg}")
            errors.append("Invalid regions format")
        else:
            print("✓ All regions are properly formatted (arrays of strings)")
    
    print()
    return len(errors) == 0


def validate_python_script():
    """Validate scrape_switch_games.py."""
    print("=" * 60)
    print("VALIDATING scrape_switch_games.py")
    print("=" * 60)
    
    try:
        with open('scrape_switch_games.py', 'r') as f:
            script_content = f.read()
        
        # Check Python syntax
        compile(script_content, 'scrape_switch_games.py', 'exec')
        print("✓ Python syntax is valid")
        
        # Check for required imports
        required_imports = ['requests', 'BeautifulSoup', 'json']
        for imp in required_imports:
            if imp in script_content:
                print(f"✓ Contains import for '{imp}'")
            else:
                print(f"⚠ Missing import for '{imp}'")
        
        print()
        return True
        
    except SyntaxError as e:
        print(f"✗ Python syntax error: {e}")
        print()
        return False
    except FileNotFoundError:
        print("✗ File not found: scrape_switch_games.py")
        print()
        return False


def validate_workflow():
    """Validate GitHub workflow."""
    print("=" * 60)
    print("VALIDATING GitHub Workflow")
    print("=" * 60)
    
    workflow_path = '.github/workflows/scrape_switch_games.yml'
    
    if not os.path.exists(workflow_path):
        print(f"⚠ Workflow file not found: {workflow_path}")
        print()
        return True  # Not critical
    
    try:
        with open(workflow_path, 'r') as f:
            workflow_content = f.read()
        print("✓ Workflow file exists")
        
        # Basic checks
        if 'workflow_dispatch' in workflow_content:
            print("✓ Manual triggering enabled (workflow_dispatch)")
        if 'schedule' in workflow_content:
            print("✓ Scheduled runs configured")
        if 'python' in workflow_content.lower():
            print("✓ Python setup included")
        if 'scrape_switch_games.py' in workflow_content:
            print("✓ Script execution configured")
        
        print()
        return True
        
    except Exception as e:
        print(f"⚠ Error reading workflow file: {e}")
        print()
        return True  # Not critical


def main():
    """Main validation function."""
    print()
    print("=" * 60)
    print("GAMES.DATABASE REPOSITORY VALIDATION")
    print("=" * 60)
    print()
    
    # Run all validations
    json_valid = validate_json_file()
    script_valid = validate_python_script()
    workflow_valid = validate_workflow()
    
    # Print summary
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if json_valid and script_valid and workflow_valid:
        print("✓ All validations passed!")
        print("✓ Switch.Games.json is valid and properly formatted")
        print("✓ Python script has valid syntax")
        print("✓ Repository is in good state")
        print("=" * 60)
        return 0
    else:
        print("✗ Some validations failed:")
        if not json_valid:
            print("  - Switch.Games.json has errors")
        if not script_valid:
            print("  - scrape_switch_games.py has errors")
        if not workflow_valid:
            print("  - GitHub workflow has issues")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
