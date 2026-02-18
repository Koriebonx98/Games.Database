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
const clearSearchBtn = document.getElementById('clearSearch');
const homeButton = document.getElementById('homeButton');
const homeButtonInfo = document.getElementById('homeButtonInfo');
const backButton = document.getElementById('backButton');
const platformTitle = document.getElementById('platformTitle');
const gamesCount = document.getElementById('gamesCount');
const mediaModal = document.getElementById('mediaModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalImage = document.getElementById('modalImage');
const modalVideo = document.getElementById('modalVideo');

// Helper function to get YouTube video ID from URL
// Supports formats: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID, youtube.com/v/ID
function getYouTubeVideoId(url) {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/|youtube\.com\/watch\?v=)([^"&?\/\s]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

// Helper function to get Title ID from a game object
// Supports multiple field names: TitleID, title_id, id
function getTitleId(game) {
    return game.TitleID || game.title_id || game.id;
}

// Debounce function to reduce excessive filtering calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Platform detection - This will be done by fetching a known list of platforms
// Since we can't iterate filesystem in the browser, we'll try to fetch known patterns
// NOTE: To add a new platform, add its name to this list and create a <Platform>.Games.json file
const KNOWN_PLATFORMS = [
    '3DS',
    'Switch',
    'PS3',
    'PS4',
    'PS5',
    'Xbox 360',
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
        } else if (Array.isArray(games.games)) {
            // Alternative format - lowercase 'games' property
            allGames = games.games;
        } else if (Array.isArray(games)) {
            // Old format - direct array
            allGames = games;
        } else {
            throw new Error('Invalid JSON format');
        }
        
        // Sort games alphabetically by Title (new format) or game_name (old format) or title (lowercase)
        allGames.sort((a, b) => {
            const nameA = (a.Title || a.game_name || a.title || '').toLowerCase();
            const nameB = (b.Title || b.game_name || b.title || '').toLowerCase();
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
        gameName.textContent = game.Title || game.game_name || game.title;
        
        const titleId = document.createElement('div');
        titleId.className = 'game-title-id';
        const titleIdValue = getTitleId(game);
        titleId.textContent = titleIdValue || '';
        
        gameItem.appendChild(gameName);
        if (titleIdValue) {
            gameItem.appendChild(titleId);
        }
        
        gamesList.appendChild(gameItem);
    });
}

// Filter games based on search input
function filterGames() {
    const searchTerm = searchBar.value.toLowerCase().trim();
    
    // Toggle clear button visibility
    if (searchTerm) {
        clearSearchBtn.classList.add('visible');
    } else {
        clearSearchBtn.classList.remove('visible');
    }
    
    if (searchTerm === '') {
        renderGames(allGames);
        return;
    }
    
    const filteredGames = allGames.filter(game => {
        const gameName = game.Title || game.game_name || game.title || '';
        // Check main title
        if (gameName.toLowerCase().includes(searchTerm)) {
            return true;
        }
        
        // Check Title ID
        const titleIdValue = getTitleId(game);
        if (titleIdValue) {
            // Convert to string and check if it matches the search term
            const titleIdStr = String(titleIdValue).toLowerCase();
            if (titleIdStr.includes(searchTerm)) {
                return true;
            }
        }
        
        // Check alternate names
        const alternateNames = game.alternate_names || game.AlternateNames || [];
        return alternateNames.some(altName => 
            altName.toLowerCase().includes(searchTerm)
        );
    });
    
    renderGames(filteredGames);
}

// Debounced version of filterGames for input events
const debouncedFilterGames = debounce(filterGames, 300);

// Clear search input and reset filter
function clearSearch() {
    searchBar.value = '';
    clearSearchBtn.classList.remove('visible');
    renderGames(allGames);
    searchBar.focus();
}

// Show game info view
function showGameInfo(game) {
    currentGame = game;
    
    // Switch to game info view
    gamesView.classList.remove('active');
    gameInfoView.classList.add('active');
    
    // Populate game info
    document.getElementById('gameInfoTitle').textContent = game.Title || game.game_name || game.title;
    
    // Update game cover image
    const gameCover = document.getElementById('game-cover');
    if (game.image && typeof game.image === 'string' && game.image.trim() !== '') {
        gameCover.src = game.image;
        gameCover.alt = `${game.Title || game.game_name || game.title} - Game Cover`;
        gameCover.style.display = 'block';
    } else {
        gameCover.style.display = 'none';
        gameCover.src = '';
        gameCover.alt = 'Game Cover';
    }
    
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
    const backgroundImagesSection = document.getElementById('backgroundImagesSection');
    
    // Title ID
    const titleIdValue = getTitleId(game);
    if (titleIdValue) {
        document.getElementById('gameInfoTitleId').textContent = titleIdValue;
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
    const description = game.Description || game.description;
    if (description) {
        document.getElementById('gameInfoDescription').textContent = description;
        descriptionSection.style.display = 'block';
    } else {
        descriptionSection.style.display = 'none';
    }
    
    // Background Images
    if (game.background_images && Array.isArray(game.background_images) && game.background_images.length > 0) {
        const backgroundImagesGallery = document.getElementById('gameInfoBackgroundImages');
        backgroundImagesGallery.innerHTML = '';
        game.background_images.forEach((imagePath, index) => {
            const imageItem = document.createElement('div');
            imageItem.className = 'background-image-item';
            
            const img = document.createElement('img');
            img.src = imagePath;
            img.alt = `${game.Title || game.game_name || game.title} - Background ${index + 1}`;
            img.loading = 'lazy';
            
            // Add click event to open modal
            imageItem.addEventListener('click', () => openImageModal(imagePath));
            
            imageItem.appendChild(img);
            backgroundImagesGallery.appendChild(imageItem);
        });
        backgroundImagesSection.style.display = 'block';
    } else {
        backgroundImagesSection.style.display = 'none';
    }
    
    // Trailers Section
    let trailersSection = document.getElementById('trailersSection');
    if (!trailersSection) {
        // Create trailers section if it doesn't exist
        trailersSection = document.createElement('div');
        trailersSection.className = 'game-info-section';
        trailersSection.id = 'trailersSection';
        trailersSection.innerHTML = '<h3>Trailers</h3><div id="gameInfoTrailers" class="background-images-gallery"></div>';
        backgroundImagesSection.parentNode.insertBefore(trailersSection, backgroundImagesSection);
    }
    
    if (game.trailers && Array.isArray(game.trailers) && game.trailers.length > 0) {
        const trailersGallery = document.getElementById('gameInfoTrailers');
        trailersGallery.innerHTML = '';
        game.trailers.forEach((trailerUrl, index) => {
            const videoId = getYouTubeVideoId(trailerUrl);
            if (videoId) {
                const trailerItem = document.createElement('div');
                trailerItem.className = 'trailer-item';
                
                // Use YouTube thumbnail
                const thumbnail = document.createElement('img');
                thumbnail.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
                thumbnail.alt = `${game.Title || game.game_name || game.title} - Trailer ${index + 1}`;
                thumbnail.className = 'trailer-thumbnail';
                thumbnail.loading = 'lazy';
                
                // Add play button overlay
                const playButton = document.createElement('div');
                playButton.className = 'trailer-play-button';
                
                // Add click event to open video modal
                trailerItem.addEventListener('click', () => openVideoModal(videoId));
                
                trailerItem.appendChild(thumbnail);
                trailerItem.appendChild(playButton);
                trailersGallery.appendChild(trailerItem);
            }
        });
        trailersSection.style.display = 'block';
    } else {
        trailersSection.style.display = 'none';
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
    clearSearchBtn.classList.remove('visible');
    allGames = [];
    currentPlatform = '';
    currentGame = null;
}

// Setup event listeners
function setupEventListeners() {
    homeButton.addEventListener('click', goHome);
    homeButtonInfo.addEventListener('click', goHome);
    backButton.addEventListener('click', goBackToGames);
    searchBar.addEventListener('input', debouncedFilterGames);
    clearSearchBtn.addEventListener('click', clearSearch);
    
    // Modal event listeners
    modalCloseBtn.addEventListener('click', closeModal);
    mediaModal.addEventListener('click', (e) => {
        // Close modal if clicking outside the content
        if (e.target === mediaModal) {
            closeModal();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus search (or just "/" like many sites)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (gamesView.classList.contains('active')) {
                searchBar.focus();
            }
        }
        // "/" to focus search (unless in an input)
        if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
            e.preventDefault();
            if (gamesView.classList.contains('active')) {
                searchBar.focus();
            }
        }
        // Escape to clear search when search bar is focused, or close modal
        if (e.key === 'Escape') {
            if (mediaModal.classList.contains('active')) {
                closeModal();
            } else if (document.activeElement === searchBar) {
                if (searchBar.value) {
                    clearSearch();
                } else {
                    searchBar.blur();
                }
            }
        }
    });
}

// Open image in modal
function openImageModal(imageSrc) {
    modalImage.src = imageSrc;
    modalImage.style.display = 'block';
    modalVideo.style.display = 'none';
    modalVideo.innerHTML = '';
    mediaModal.classList.add('active');
}

// Open video in modal
function openVideoModal(videoId) {
    modalImage.style.display = 'none';
    modalVideo.style.display = 'block';
    
    // Create YouTube embed iframe (autoplay for user-initiated action)
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    iframe.allowFullscreen = true;
    
    modalVideo.innerHTML = '';
    modalVideo.appendChild(iframe);
    mediaModal.classList.add('active');
}

// Close modal
function closeModal() {
    mediaModal.classList.remove('active');
    modalImage.src = '';
    modalImage.style.display = 'none';
    modalVideo.style.display = 'none';
    modalVideo.innerHTML = '';
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
