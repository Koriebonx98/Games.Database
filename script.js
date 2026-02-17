// State management
let allGames = [];
let currentPlatform = '';
let currentGame = null;

// DOM elements
const platformView = document.getElementById('platformView');
const gamesView = document.getElementById('gamesView');
const gameInfoView = document.getElementById('gameInfoView');
const platformButtons = document.getElementById('platformButtons');
const gamesList = document.getElementById('gamesList');
const searchBar = document.getElementById('searchBar');
const homeButton = document.getElementById('homeButton');
const homeButtonInfo = document.getElementById('homeButtonInfo');
const backButton = document.getElementById('backButton');
const platformTitle = document.getElementById('platformTitle');
const gamesCount = document.getElementById('gamesCount');

// Platform detection - This will be done by fetching a known list of platforms
// Since we can't iterate filesystem in the browser, we'll try to fetch known patterns
// NOTE: To add a new platform, add its name to this list and create a <Platform>.Games.json file
const KNOWN_PLATFORMS = [
    '3DS',
    'Switch',
    'PS3',
    'PS4',
    'PS5',
    'Xbox',
    'PC',
    'Wii',
    'WiiU',
    'GameBoy',
    'DS',
    'PSP',
    'Vita'
];

// Initialize the application
async function init() {
    await detectPlatforms();
    setupEventListeners();
}

// Detect available platforms by checking for JSON files
async function detectPlatforms() {
    const availablePlatforms = [];
    
    for (const platform of KNOWN_PLATFORMS) {
        try {
            const response = await fetch(`${platform}.Games.json`);
            if (response.ok) {
                availablePlatforms.push(platform);
            }
        } catch (error) {
            // Platform file doesn't exist, skip it
            console.log(`Platform ${platform} not found`);
        }
    }

    if (availablePlatforms.length === 0) {
        const errorMsg = document.createElement('p');
        errorMsg.className = 'error';
        errorMsg.textContent = 'No platform files found. Please add JSON files following the naming convention: <Platform>.Games.json';
        platformButtons.innerHTML = '';
        platformButtons.appendChild(errorMsg);
    } else {
        renderPlatformButtons(availablePlatforms);
    }
}

// Render platform buttons
function renderPlatformButtons(platforms) {
    platformButtons.innerHTML = '';
    
    platforms.forEach(platform => {
        const button = document.createElement('button');
        button.className = 'platform-btn';
        button.textContent = platform;
        button.onclick = () => loadPlatform(platform);
        platformButtons.appendChild(button);
    });
}

// Load games for a specific platform
async function loadPlatform(platform) {
    currentPlatform = platform;
    platformTitle.textContent = `${platform} Games`;
    
    // Switch to games view
    platformView.classList.remove('active');
    gamesView.classList.add('active');
    
    // Show loading state
    gamesList.innerHTML = '<p class="loading">Loading games...</p>';
    
    try {
        const response = await fetch(`${platform}.Games.json`);
        if (!response.ok) {
            throw new Error('Failed to load games');
        }
        
        const games = await response.json();
        
        // Check if the JSON has the new format with Platform and Games properties
        if (games.Platform && Array.isArray(games.Games)) {
            allGames = games.Games;
        } else if (Array.isArray(games)) {
            // Old format - direct array
            allGames = games;
        } else {
            throw new Error('Invalid JSON format');
        }
        
        // Sort games alphabetically by Title (new format) or game_name (old format)
        allGames.sort((a, b) => {
            const nameA = (a.Title || a.game_name || '').toLowerCase();
            const nameB = (b.Title || b.game_name || '').toLowerCase();
            return nameA.localeCompare(nameB);
        });
        
        renderGames(allGames);
    } catch (error) {
        gamesList.innerHTML = `<p class="error">Failed to load games: ${error.message}</p>`;
    }
}

// Render games list
function renderGames(games) {
    if (games.length === 0) {
        gamesList.innerHTML = '<p class="no-games">No games found</p>';
        gamesCount.textContent = '';
        return;
    }
    
    gamesCount.textContent = `Showing ${games.length} game${games.length !== 1 ? 's' : ''}`;
    
    gamesList.innerHTML = '';
    games.forEach((game, index) => {
        const gameItem = document.createElement('div');
        gameItem.className = 'game-item';
        gameItem.onclick = () => showGameInfo(game);
        
        const gameName = document.createElement('div');
        gameName.className = 'game-name';
        gameName.textContent = game.Title || game.game_name;
        
        const titleId = document.createElement('div');
        titleId.className = 'game-title-id';
        titleId.textContent = game.title_id || '';
        
        gameItem.appendChild(gameName);
        if (game.title_id) {
            gameItem.appendChild(titleId);
        }
        
        gamesList.appendChild(gameItem);
    });
}

// Filter games based on search input
function filterGames() {
    const searchTerm = searchBar.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        renderGames(allGames);
        return;
    }
    
    const filteredGames = allGames.filter(game => {
        const gameName = game.Title || game.game_name || '';
        // Check main title
        if (gameName.toLowerCase().includes(searchTerm)) {
            return true;
        }
        // Check alternate names
        const alternateNames = game.alternate_names || game.AlternateNames || [];
        return alternateNames.some(altName => 
            altName.toLowerCase().includes(searchTerm)
        );
    });
    
    renderGames(filteredGames);
}

// Show game info view
function showGameInfo(game) {
    currentGame = game;
    
    // Switch to game info view
    gamesView.classList.remove('active');
    gameInfoView.classList.add('active');
    
    // Populate game info
    document.getElementById('gameInfoTitle').textContent = game.Title || game.game_name;
    
    // Show or hide sections based on available data
    const titleIdSection = document.getElementById('titleIdSection');
    const regionSection = document.getElementById('regionSection');
    const releaseDateSection = document.getElementById('releaseDateSection');
    const distributionMethodSection = document.getElementById('distributionMethodSection');
    const versionsSection = document.getElementById('versionsSection');
    const cartridgeDescriptionSection = document.getElementById('cartridgeDescriptionSection');
    const typeSection = document.getElementById('typeSection');
    const alternateNamesSection = document.getElementById('alternateNamesSection');
    const descriptionSection = document.getElementById('descriptionSection');
    
    // Title ID
    if (game.title_id) {
        document.getElementById('gameInfoTitleId').textContent = game.title_id;
        titleIdSection.style.display = 'block';
    } else {
        titleIdSection.style.display = 'none';
    }
    
    // Region
    if (game.Region || game.region) {
        document.getElementById('gameInfoRegion').textContent = game.Region || game.region;
        regionSection.style.display = 'block';
    } else {
        regionSection.style.display = 'none';
    }
    
    // Release Date / Minimum OS Version
    if (game.ReleaseDate || game.min_os_version) {
        let displayText = game.ReleaseDate;
        if (!displayText && game.min_os_version) {
            displayText = `Minimum OS: ${game.min_os_version}`;
        }
        document.getElementById('gameInfoReleaseDate').textContent = displayText;
        releaseDateSection.style.display = 'block';
    } else {
        releaseDateSection.style.display = 'none';
    }
    
    // Distribution Method
    if (game.distribution_method) {
        document.getElementById('gameInfoDistribution').textContent = game.distribution_method;
        distributionMethodSection.style.display = 'block';
    } else {
        distributionMethodSection.style.display = 'none';
    }
    
    // Versions
    if (game.versions) {
        document.getElementById('gameInfoVersions').textContent = game.versions;
        versionsSection.style.display = 'block';
    } else {
        versionsSection.style.display = 'none';
    }
    
    // Cartridge Description
    if (game.cartridge_description) {
        document.getElementById('gameInfoCartridge').textContent = game.cartridge_description;
        cartridgeDescriptionSection.style.display = 'block';
    } else {
        cartridgeDescriptionSection.style.display = 'none';
    }
    
    // Type
    if (game.type) {
        document.getElementById('gameInfoType').textContent = game.type;
        typeSection.style.display = 'block';
    } else {
        typeSection.style.display = 'none';
    }
    
    // Alternate Names
    if ((game.alternate_names && game.alternate_names.length > 0) || 
        (game.AlternateNames && game.AlternateNames.length > 0)) {
        const alternateNamesList = document.getElementById('gameInfoAlternateNames');
        alternateNamesList.innerHTML = '';
        const names = game.alternate_names || game.AlternateNames;
        names.forEach(name => {
            const li = document.createElement('li');
            li.textContent = name;
            alternateNamesList.appendChild(li);
        });
        alternateNamesSection.style.display = 'block';
    } else {
        alternateNamesSection.style.display = 'none';
    }
    
    // Description
    if (game.Description) {
        document.getElementById('gameInfoDescription').textContent = game.Description;
        descriptionSection.style.display = 'block';
    } else {
        descriptionSection.style.display = 'none';
    }
}

// Go back to games list
function goBackToGames() {
    gameInfoView.classList.remove('active');
    gamesView.classList.add('active');
    currentGame = null;
}

// Go back to platform selection
function goHome() {
    gamesView.classList.remove('active');
    gameInfoView.classList.remove('active');
    platformView.classList.add('active');
    searchBar.value = '';
    allGames = [];
    currentPlatform = '';
    currentGame = null;
}

// Setup event listeners
function setupEventListeners() {
    homeButton.addEventListener('click', goHome);
    homeButtonInfo.addEventListener('click', goHome);
    backButton.addEventListener('click', goBackToGames);
    searchBar.addEventListener('input', filterGames);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
