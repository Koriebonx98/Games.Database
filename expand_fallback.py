import json

# Load current fallback data
with open('ps3_games_fallback.json', 'r') as f:
    data = json.load(f)

# Add many more games to make it comprehensive
additional_games = [
    # Sports Games
    {"Title": "FIFA 13", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-09-25"},
    {"Title": "FIFA 14", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-09-24"},
    {"Title": "NBA 2K13", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-10-02"},
    {"Title": "NBA 2K14", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-10-01"},
    {"Title": "Madden NFL 13", "Region": "USA", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-08-28"},
    {"Title": "MLB The Show 13", "Region": "USA", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-03-05"},
    
    # Racing Games
    {"Title": "Need for Speed: Most Wanted", "Region": "USA EUR", "AlternateNames": ["NFS MW"], "Description": "", "ReleaseDate": "2012-10-30"},
    {"Title": "Need for Speed: Hot Pursuit", "Region": "USA EUR", "AlternateNames": ["NFS HP"], "Description": "", "ReleaseDate": "2010-11-16"},
    {"Title": "Burnout Paradise", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2008-01-22"},
    
    # RPGs
    {"Title": "The Elder Scrolls IV: Oblivion", "Region": "USA EUR", "AlternateNames": ["Oblivion"], "Description": "", "ReleaseDate": "2007-03-20"},
    {"Title": "Fallout 3", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2008-10-28"},
    {"Title": "Fallout: New Vegas", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2010-10-19"},
    {"Title": "Dragon Age: Origins", "Region": "USA EUR", "AlternateNames": ["DA Origins"], "Description": "", "ReleaseDate": "2009-11-03"},
    {"Title": "Dragon Age II", "Region": "USA EUR", "AlternateNames": ["DA2"], "Description": "", "ReleaseDate": "2011-03-08"},
    {"Title": "Tales of Xillia", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2011-09-08"},
    {"Title": "Valkyria Chronicles", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2008-04-24"},
    
    # Platformers
    {"Title": "Ratchet & Clank Future: Tools of Destruction", "Region": "USA EUR", "AlternateNames": ["R&C ToD"], "Description": "", "ReleaseDate": "2007-10-23"},
    {"Title": "Ratchet & Clank Future: A Crack in Time", "Region": "USA EUR", "AlternateNames": ["R&C CiT"], "Description": "", "ReleaseDate": "2009-10-27"},
    {"Title": "Sonic Generations", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2011-11-01"},
    {"Title": "Rayman Legends", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-09-03"},
    
    # Fighting Games
    {"Title": "Street Fighter IV", "Region": "USA EUR JPN", "AlternateNames": ["SF4"], "Description": "", "ReleaseDate": "2009-02-12"},
    {"Title": "Super Street Fighter IV", "Region": "USA EUR JPN", "AlternateNames": ["SSF4"], "Description": "", "ReleaseDate": "2010-04-27"},
    {"Title": "Mortal Kombat", "Region": "USA EUR", "AlternateNames": ["MK"], "Description": "", "ReleaseDate": "2011-04-19"},
    {"Title": "Tekken 6", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2009-10-27"},
    
    # Shooters
    {"Title": "Battlefield 3", "Region": "USA EUR", "AlternateNames": ["BF3"], "Description": "", "ReleaseDate": "2011-10-25"},
    {"Title": "Battlefield 4", "Region": "USA EUR", "AlternateNames": ["BF4"], "Description": "", "ReleaseDate": "2013-10-29"},
    {"Title": "Borderlands", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2009-10-20"},
    {"Title": "Borderlands 2", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-09-18"},
    {"Title": "Crysis 2", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2011-03-22"},
    {"Title": "Far Cry 3", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-11-29"},
    
    # Adventure Games
    {"Title": "Beyond: Two Souls", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-10-08"},
    {"Title": "Journey", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-03-13"},
    {"Title": "Infamous: Festival of Blood", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2011-10-25"},
    {"Title": "Tomb Raider", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-03-05"},
    
    # Strategy/Simulation
    {"Title": "XCOM: Enemy Unknown", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-10-09"},
    {"Title": "The Sims 3", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2010-10-26"},
    
    # Horror
    {"Title": "Resident Evil 5", "Region": "USA EUR JPN", "AlternateNames": ["RE5"], "Description": "", "ReleaseDate": "2009-03-13"},
    {"Title": "Resident Evil 6", "Region": "USA EUR JPN", "AlternateNames": ["RE6"], "Description": "", "ReleaseDate": "2012-10-02"},
    {"Title": "Silent Hill: Downpour", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-03-13"},
    
    # More exclusives
    {"Title": "The ICO & Shadow of the Colossus Collection", "Region": "USA EUR JPN", "AlternateNames": ["ICO Collection"], "Description": "", "ReleaseDate": "2011-09-22"},
    {"Title": "Sly Cooper: Thieves in Time", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-02-05"},
    {"Title": "God of War: Collection", "Region": "USA EUR", "AlternateNames": ["GoW Collection"], "Description": "", "ReleaseDate": "2009-11-17"},
    {"Title": "Twisted Metal", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-02-14"},
    {"Title": "ModNation Racers", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2010-05-25"},
    
    # More popular titles
    {"Title": "Dishonored", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-10-09"},
    {"Title": "Mirror's Edge", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2008-11-11"},
    {"Title": "Just Cause 2", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2010-03-23"},
    {"Title": "Sleeping Dogs", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-08-14"},
    {"Title": "Max Payne 3", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-05-15"},
    {"Title": "Hitman: Absolution", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-11-20"},
    {"Title": "Deus Ex: Human Revolution", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2011-08-23"},
    
    # Japanese Games
    {"Title": "Persona 5", "Region": "JPN USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2016-09-15"},
    {"Title": "Persona 4 Arena", "Region": "JPN USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-07-26"},
    {"Title": "Catherine", "Region": "JPN USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2011-02-17"},
    {"Title": "Yakuza 3", "Region": "JPN USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2009-02-26"},
    {"Title": "Yakuza 4", "Region": "JPN USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2010-03-18"},
    
    # More Call of Duty titles
    {"Title": "Call of Duty: World at War", "Region": "USA EUR", "AlternateNames": ["CoD WaW"], "Description": "", "ReleaseDate": "2008-11-11"},
    {"Title": "Call of Duty: Ghosts", "Region": "USA EUR", "AlternateNames": ["CoD Ghosts"], "Description": "", "ReleaseDate": "2013-11-05"},
    
    # More racing
    {"Title": "F1 2012", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-09-18"},
    {"Title": "WipEout HD", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2008-09-25"},
    
    # Music/Rhythm
    {"Title": "Rock Band 3", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2010-10-26"},
    {"Title": "Guitar Hero III: Legends of Rock", "Region": "USA EUR", "AlternateNames": ["GH3"], "Description": "", "ReleaseDate": "2007-10-28"},
    
    # Stealth
    {"Title": "Splinter Cell: Blacklist", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-08-20"},
    {"Title": "Metal Gear Solid V: Ground Zeroes", "Region": "USA EUR JPN", "AlternateNames": ["MGSV GZ"], "Description": "", "ReleaseDate": "2014-03-18"},
    
    # More action titles
    {"Title": "Dante's Inferno", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2010-02-09"},
    {"Title": "Castlevania: Lords of Shadow", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2010-10-05"},
    {"Title": "Bayonetta", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2009-10-29"},
    {"Title": "Ninja Gaiden Sigma", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2007-06-14"},
    
    # HD Collections
    {"Title": "Metal Gear Solid HD Collection", "Region": "USA EUR JPN", "AlternateNames": ["MGS HD"], "Description": "", "ReleaseDate": "2011-11-08"},
    {"Title": "Devil May Cry HD Collection", "Region": "USA EUR JPN", "AlternateNames": ["DMC HD"], "Description": "", "ReleaseDate": "2012-03-22"},
    {"Title": "Prince of Persia Trilogy", "Region": "USA EUR", "AlternateNames": ["PoP Trilogy"], "Description": "", "ReleaseDate": "2010-11-19"},
    
    # Arcade/Indie
    {"Title": "Braid", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2008-08-06"},
    {"Title": "Limbo", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2011-07-19"},
    {"Title": "Flower", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2009-02-12"},
    
    # More shooters
    {"Title": "Killzone HD", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-10-23"},
    {"Title": "Resistance: Burning Skies", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2012-05-29"},
    {"Title": "Bulletstorm", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2011-02-22"},
    
    # More popular cross-platform
    {"Title": "Saints Row: The Third", "Region": "USA EUR", "AlternateNames": ["SR3"], "Description": "", "ReleaseDate": "2011-11-15"},
    {"Title": "Saints Row IV", "Region": "USA EUR", "AlternateNames": ["SR4"], "Description": "", "ReleaseDate": "2013-08-20"},
    {"Title": "Minecraft", "Region": "USA EUR JPN", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-12-17"},
    {"Title": "Terraria", "Region": "USA EUR", "AlternateNames": [], "Description": "", "ReleaseDate": "2013-03-26"},
    
    # More Final Fantasy
    {"Title": "Final Fantasy XIII-2", "Region": "USA EUR JPN", "AlternateNames": ["FF XIII-2"], "Description": "", "ReleaseDate": "2011-12-15"},
    {"Title": "Lightning Returns: Final Fantasy XIII", "Region": "USA EUR JPN", "AlternateNames": ["LR FFXIII"], "Description": "", "ReleaseDate": "2013-11-21"},
    {"Title": "Final Fantasy X/X-2 HD Remaster", "Region": "USA EUR JPN", "AlternateNames": ["FFX HD"], "Description": "", "ReleaseDate": "2013-12-26"},
]

# Add games to the existing list
data["Games"].extend(additional_games)

# Sort by title
data["Games"] = sorted(data["Games"], key=lambda x: x["Title"])

# Save back to file
with open('ps3_games_fallback.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated fallback data with {len(data['Games'])} total games")
