// Global variables
let platformsData = {};
let currentPlatform = '';
let allGames = [];

// DOM elements
const platformView = document.getElementById('platform-view');
const gamesView = document.getElementById('games-view');
const platformButtons = document.getElementById('platform-buttons');
const gamesList = document.getElementById('games-list');
const platformTitle = document.getElementById('platform-title');
const homeBtn = document.getElementById('home-btn');
const searchBar = document.getElementById('search-bar');

// Load platforms from JSON file
async function loadPlatforms() {
    try {
        const response = await fetch('platforms.json');
        if (!response.ok) {
            throw new Error(`Failed to load platforms.json: ${response.status} ${response.statusText}`);
        }
        platformsData = await response.json();
        displayPlatformButtons();
    } catch (error) {
        console.error('Error loading platforms:', error);
        platformButtons.innerHTML = `<p class="no-results">Error loading platforms: ${error.message}</p>`;
    }
}

// Display platform buttons
function displayPlatformButtons() {
    platformButtons.innerHTML = '';
    
    const platforms = Object.keys(platformsData);
    
    if (platforms.length === 0) {
        platformButtons.innerHTML = '<p class="no-results">No platforms available.</p>';
        return;
    }
    
    platforms.forEach(platform => {
        const button = document.createElement('button');
        button.className = 'platform-btn';
        button.textContent = platform;
        button.addEventListener('click', () => showGames(platform));
        platformButtons.appendChild(button);
    });
}

// Show games for selected platform
function showGames(platform) {
    currentPlatform = platform;
    allGames = platformsData[platform] || [];
    
    // Sort games alphabetically (A-Z)
    allGames.sort((a, b) => a.localeCompare(b));
    
    platformTitle.textContent = platform;
    searchBar.value = '';
    
    displayGames(allGames);
    
    // Switch views
    platformView.classList.remove('active');
    gamesView.classList.add('active');
}

// Display games in the list
function displayGames(games) {
    gamesList.innerHTML = '';
    
    if (games.length === 0) {
        gamesList.innerHTML = '<p class="no-results">No games found.</p>';
        return;
    }
    
    games.forEach(game => {
        const gameItem = document.createElement('div');
        gameItem.className = 'game-item';
        
        const gameTitle = document.createElement('h3');
        gameTitle.textContent = game;
        
        gameItem.appendChild(gameTitle);
        gamesList.appendChild(gameItem);
    });
}

// Go back to platform selection
function goHome() {
    platformView.classList.add('active');
    gamesView.classList.remove('active');
    searchBar.value = '';
}

// Filter games based on search input
function filterGames() {
    const searchTerm = searchBar.value.toLowerCase();
    
    if (searchTerm === '') {
        displayGames(allGames);
        return;
    }
    
    const filteredGames = allGames.filter(game => 
        game.toLowerCase().includes(searchTerm)
    );
    
    displayGames(filteredGames);
}

// Event listeners
homeBtn.addEventListener('click', goHome);
searchBar.addEventListener('input', filterGames);

// Initialize the app
loadPlatforms();
