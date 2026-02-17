import requests
import json

# Test various potential data sources for PS3 games
sources = [
    "https://api.github.com/repos/psdevwiki/psdevwiki.github.io/contents/",
    "https://raw.githubusercontent.com/FlaviusHouk/ps3-game-list/main/",
    "https://www.giantbomb.com/api/games/",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for url in sources:
    try:
        print(f"Testing: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Content preview: {response.text[:200]}")
        print()
    except Exception as e:
        print(f"  Error: {e}\n")
