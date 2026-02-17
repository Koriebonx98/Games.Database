import requests
from bs4 import BeautifulSoup

# Try to get PS3 games from Wikipedia
urls = [
    "https://en.wikipedia.org/wiki/List_of_PlayStation_3_games",
    "https://en.m.wikipedia.org/wiki/List_of_PlayStation_3_games",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for url in urls:
    try:
        print(f"Testing: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            # Find tables
            tables = soup.find_all('table', {'class': 'wikitable'})
            print(f"  Found {len(tables)} wikitable(s)")
            if tables:
                # Check first table structure
                rows = tables[0].find_all('tr')[:5]
                print(f"  First table has {len(tables[0].find_all('tr'))} rows")
                print("  Sample rows:")
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    print(f"    {[c.get_text(strip=True)[:30] for c in cells]}")
        print()
    except Exception as e:
        print(f"  Error: {e}\n")
