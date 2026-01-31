# Instructions for Scraping Nintendo Switch Game Data

## Overview

This repository contains a web scraper (`scrape_switch_games.py`) that extracts Nintendo Switch game names and title IDs from the switchbrew.org website.

## Current Status

✅ **Completed:**
- Python scraper script created
- JSON file format defined
- Sample data added to Switch.Games.json (12 popular games)
- README documentation created

⚠️ **Limitation:**
The current sandbox/CI environment has restricted internet access and cannot connect to external websites including switchbrew.org. To get the complete dataset, the scraper needs to be run from an environment with unrestricted internet access.

## How to Get the Complete Dataset

### Option 1: Run the Scraper Locally (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/Koriebonx98/Games.Database.git
   cd Games.Database
   ```

2. Install dependencies:
   ```bash
   pip install requests beautifulsoup4 lxml
   ```

3. Run the scraper:
   ```bash
   python3 scrape_switch_games.py
   ```

4. The script will:
   - Fetch the latest game list from switchbrew.org
   - Parse all games and their title IDs
   - Update Switch.Games.json with the complete dataset
   - Display a summary of extracted games

5. Commit and push the updated file:
   ```bash
   git add Switch.Games.json
   git commit -m "Update Switch games database with complete dataset"
   git push
   ```

### Option 2: Manual Data Entry

If you prefer to manually compile the data:

1. Visit https://switchbrew.org/w/index.php?title=Title_list/Games&mobileaction=toggle_view_desktop
2. Copy game names and title IDs from the tables
3. Add them to Switch.Games.json following this format:
   ```json
   {
     "title_id": "01007EF00011E000",
     "game_name": "The Legend of Zelda: Breath of the Wild"
   }
   ```

### Option 3: Use GitHub Actions (Advanced)

You could set up a GitHub Actions workflow to run the scraper periodically and automatically update the database. This would require:
- A workflow file (.github/workflows/scrape.yml)
- Proper permissions for the workflow to commit changes
- Scheduled runs (e.g., weekly or monthly)

## Data Format

Each game entry in Switch.Games.json has:
- **title_id**: 16-character hexadecimal identifier (e.g., "01007EF00011E000")
- **game_name**: Official game title

Title IDs follow the Nintendo Switch format:
- First 4 chars: "0100" (indicates retail application)
- Next 12 chars: Unique game identifier
- Base games typically end in "0000"

## Troubleshooting

**Error: "Failed to resolve 'switchbrew.org'"**
- This means the script cannot access the internet
- Run the script from a local machine or server with internet access
- Check firewall/proxy settings

**Error: "No games were extracted"**
- The website structure may have changed
- Check the switchbrew.org website manually
- The HTML parsing logic may need to be updated

**Script runs but gets 0 games:**
- Verify the URL is still correct
- Check if the website requires authentication or has rate limiting
- Review the HTML structure of the page

## Next Steps

1. Run the scraper from an environment with internet access
2. Verify the extracted data is complete and accurate
3. Consider setting up automated updates
4. Optionally add more metadata (release dates, publishers, etc.)

## Support

If you encounter issues:
1. Check that you have internet access
2. Verify Python and dependencies are installed
3. Try running with verbose output to see what's happening
4. Check the switchbrew.org website to ensure it's accessible

## Additional Resources

- [Switchbrew Title List](https://switchbrew.org/wiki/Title_list/Games)
- [Nintendo Switch Title ID Format](https://switchbrew.org/wiki/Title_list)
- [Switch Game Database Examples](https://github.com/fmartingr/switch-games-json)
