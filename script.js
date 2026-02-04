// State management
let allGames = [];
let currentPlatform = '';

// DOM elements
const platformView = document.getElementById('platformView');
const gamesView = document.getElementById('gamesView');
const platformButtons = document.getElementById('platformButtons');
const gamesList = document.getElementById('gamesList');
const searchBar = document.getElementById('searchBar');
const homeButton = document.getElementById('homeButton');
const platformTitle = document.getElementById('platformTitle');
const gamesCount = document.getElementById('gamesCount');

// Platform detection - This will be done by fetching a known list of platforms
// Since we can't iterate filesystem in the browser, we'll try to fetch known patterns
// NOTE: To add a new platform, add its name to this list and create a <Platform>.Games.json file
// For example, to add PS3 support, add 'PS3' to this array and create PS3.Games.json
const KNOWN_PLATFORMS = [
    '3DS',
    'Switch',
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
        allGames = games;
        
        // Sort games alphabetically by game_name
        allGames.sort((a, b) => {
            const nameA = a.game_name.toLowerCase();
            const nameB = b.game_name.toLowerCase();
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
    games.forEach(game => {
        const gameItem = document.createElement('div');
        gameItem.className = 'game-item';
        
        const gameName = document.createElement('div');
        gameName.className = 'game-name';
        gameName.textContent = game.game_name;
        
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
    
    const filteredGames = allGames.filter(game => 
        game.game_name.toLowerCase().includes(searchTerm)
    );
    
    renderGames(filteredGames);
}

// Go back to platform selection
function goHome() {
    gamesView.classList.remove('active');
    platformView.classList.add('active');
    searchBar.value = '';
    allGames = [];
    currentPlatform = '';
}

// Setup event listeners
function setupEventListeners() {
    homeButton.addEventListener('click', goHome);
    searchBar.addEventListener('input', filterGames);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
