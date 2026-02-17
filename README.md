# Games.Database

## Overview

This repository contains a games database with a web interface for browsing games across multiple platforms. It includes scrapers for collecting PlayStation 3 and Nintendo Switch game data, and a dynamic website for viewing games from any platform.

## Features

### Web Interface

A responsive website that allows you to browse games across different platforms:

- **Dynamic Platform Detection**: Automatically discovers all available platform JSON files
- **Searchable Games Library**: Filter games by title in real-time
- **Detailed Game Information**: Click on any game to view detailed information including:
  - Title
  - Region
  - Alternate Names
  - Description
  - Release Date (if available)
- **Intuitive Navigation**: Navigate between platform selection, game list, and game details with back buttons
- **Alphabetically Sorted**: All games are displayed in A-Z order
- **Responsive Design**: Works on desktop and mobile devices

To view the website, simply open `index.html` in a web browser or host it on a web server.

### Data Scrapers

#### PlayStation 3 Games Database Scraper

A Python script to scrape PS3 game data from gametdb.com and store it in JSON format. Features:

- **Pagination Handling**: Automatically loops through all available pages (up to 108 pages)
- **Retry Logic**: Implements retry mechanism with configurable attempts for failed requests
- **Early Exit**: Stops after 3 consecutive failures to avoid long waits when site is inaccessible
- **Comprehensive Logging**: Progress tracking with page numbers, success/failure counts, and error messages
- **Fallback Data**: Uses a curated dataset of 133+ popular PS3 games when live scraping fails
- **Automatic Merging**: Combines scraped data with fallback data for comprehensive coverage
- **Standardized Format**: Outputs data in the same format as other platforms (PS4, Switch)

**Dependencies:**
```bash
pip install beautifulsoup4 lxml requests
```

**Usage:**
```bash
python3 scrape_ps3_games.py
```

The script will:
1. Attempt to scrape all pages from gametdb.com
2. Display progress with logging (page number, games extracted)
3. Fallback to curated dataset if scraping fails due to network restrictions
4. Save the combined data to `PS3.Games.json`

#### Nintendo Switch Games Database Scraper

A Python script to scrape Nintendo Switch game data from switchbrew.org and store it in JSON format.

## Files

### Website Files

- `index.html` - Main webpage with platform selection and games view
- `style.css` - Styling for the website
- `script.js` - JavaScript for dynamic platform detection and game display

### Data Files

- `scrape_ps3_games.py` - Python script that scrapes PS3 game data from gametdb.com
- `PS3.Games.json` - JSON file containing PlayStation 3 game data
- `ps3_games_fallback.json` - Fallback dataset with 133+ curated PS3 games
- `scrape_switch_games.py` - Python script that scrapes game data from switchbrew.org
- `Switch.Games.json` - JSON file containing Nintendo Switch game names and title IDs

## Usage

### Viewing the Website

1. Open `index.html` in a web browser
2. Select a platform to view its games
3. Use the search bar to filter games by title
4. Click "Home" to return to platform selection

For local development with a web server:
```bash
# Python 3
python3 -m http.server 8000

# Then open http://localhost:8000 in your browser
```

### Adding New Platforms

To add a new platform to the website:

1. Create a JSON file following the naming convention: `<Platform>.Games.json`
2. Add the platform name to the `KNOWN_PLATFORMS` array in `script.js`
3. The JSON file should use one of the following formats:

#### New Format (with detailed game information):
```json
{
  "Platform": "Switch",
  "Games": [
    {
      "Title": "Game A",
      "Region": "US",
      "AlternateNames": ["Alt Game A", "Game A+ Edition"],
      "Description": "A brief description of Game A.",
      "ReleaseDate": "2020-12-01"
    },
    {
      "Title": "Game B",
      "Region": "EU",
      "AlternateNames": [],
      "Description": "A brief description of Game B.",
      "ReleaseDate": "2021-06-15"
    }
  ]
}
```

#### Legacy Format (basic game list):
```json
[
  {
    "title_id": "GAME-001",
    "game_name": "Example Game"
  }
]
```

**Field Descriptions:**
- `Title` (required): The official game title
- `Region` (optional): The region code (e.g., "US", "EU", "JP")
- `AlternateNames` (optional): Array of alternative names for the game
- `Description` (optional): A brief description of the game
- `ReleaseDate` (optional): Release date in YYYY-MM-DD format
- `title_id` (optional): Platform-specific title identifier

**Note:** The website supports both the new detailed format and the legacy format for backward compatibility. When using the new format, clicking on a game will display its detailed information.

### Running the Switch Games Scraper

- Python 3.6 or higher
- Required packages: `requests`, `beautifulsoup4`, `lxml`

### Installation

Install the required Python packages for the scraper:

```bash
pip install requests beautifulsoup4 lxml
```

### Running the Scraper

To scrape the latest Nintendo Switch game data from switchbrew.org:

```bash
python3 scrape_switch_games.py
```

This will:
1. Fetch the game list from https://switchbrew.org/w/index.php?title=Title_list/Games&mobileaction=toggle_view_desktop
2. Parse the HTML tables to extract game names and title IDs
3. Save the data to `Switch.Games.json`

### Output Format

The `Switch.Games.json` file contains an array of game objects with the following structure:

```json
[
  {
    "title_id": "01007EF00011E000",
    "game_name": "The Legend of Zelda: Breath of the Wild"
  },
  {
    "title_id": "01006F8002326000",
    "game_name": "Animal Crossing: New Horizons"
  }
]
```

### Title ID Format

Nintendo Switch title IDs are 16-character hexadecimal identifiers:
- Format: `0100NNNNMMMM0000`
- First 4 digits (`0100`): Indicates a retail Nintendo Switch application
- Next 8 digits: Unique identifier assigned by Nintendo
- Last 4 digits (`0000`): Base game (updates and DLC use different endings)

## Important Notes

### Network Requirements

This script requires **unrestricted internet access** to switchbrew.org. If you're running this in a restricted environment (such as certain CI/CD systems or sandboxed environments), you may encounter connection errors.

### Troubleshooting

If you see connection errors:
1. Ensure you have internet access
2. Check that switchbrew.org is accessible from your network
3. Try running the script from a different network/environment
4. Verify that no firewall or proxy is blocking the connection

### Data Freshness

The switchbrew.org Title list is community-maintained and updated regularly. Re-run the scraper periodically to get the latest game additions.

## Contributing

To update the game database:
1. Run `python3 scrape_switch_games.py`
2. Review the generated `Switch.Games.json`
3. Commit the updated file to the repository

## License

This is a data collection tool. The scraped data comes from switchbrew.org, which is a community resource. Please respect the source's terms of use.

## References

- [Switchbrew Title List](https://switchbrew.org/wiki/Title_list/Games)
- [Nintendo Switch Title ID Structure](https://switchbrew.org/wiki/Title_list)