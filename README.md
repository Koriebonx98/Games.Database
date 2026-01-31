# Games.Database

## Nintendo Switch Games Database Scraper

This repository contains a script to scrape Nintendo Switch game data from switchbrew.org and store it in a JSON format.

## Files

- `scrape_switch_games.py` - Python script that scrapes game data from switchbrew.org
- `Switch.Games.json` - JSON file containing Nintendo Switch game names and title IDs

## Usage

### Prerequisites

- Python 3.6 or higher
- Required packages: `requests`, `beautifulsoup4`, `lxml`

### Installation

```bash
pip install requests beautifulsoup4 lxml
```

### Running the Scraper

To scrape the latest game data from switchbrew.org:

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