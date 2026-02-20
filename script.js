// State management
let allGames = [];
let currentPlatform = '';
let currentGame = null;
let currentMediaItems = [];
let currentMediaIndex = 0;

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
const modalNavPrev = document.getElementById('modalNavPrev');
const modalNavNext = document.getElementById('modalNavNext');

// Helper function to get YouTube video ID from URL
// Supports formats: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID, youtube.com/v/ID
function getYouTubeVideoId(url) {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/|youtube\.com\/watch\?v=)([^"&?\/\s]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

// Helper function to get Title ID from a game object
// Supports multiple field names: TitleID, title_id, titleid, id
function getTitleId(game) {
    return game.TitleID || game.title_id || game.titleid || game.id;
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
    
    // Unified Media Section (Trailers + Images)
    const mediaSection = document.getElementById('mediaSection');
    const mediaItems = [];
    
    // Add trailers first
    if (game.trailers && Array.isArray(game.trailers) && game.trailers.length > 0) {
        game.trailers.forEach((trailerUrl, index) => {
            const videoId = getYouTubeVideoId(trailerUrl);
            if (videoId) {
                mediaItems.push({
                    type: 'video',
                    videoId: videoId,
                    index: mediaItems.length
                });
            }
        });
    }
    
    // Add images
    if (game.background_images && Array.isArray(game.background_images) && game.background_images.length > 0) {
        game.background_images.forEach((imagePath, index) => {
            mediaItems.push({
                type: 'image',
                src: imagePath,
                index: mediaItems.length,
                screenshotNumber: index + 1  // Track actual screenshot number
            });
        });
    }
    
    if (mediaItems.length > 0) {
        const mediaGallery = document.getElementById('gameInfoMedia');
        mediaGallery.innerHTML = '';
        
        mediaItems.forEach((mediaItem, index) => {
            const mediaItemDiv = document.createElement('div');
            mediaItemDiv.className = 'media-item';
            
            if (mediaItem.type === 'video') {
                // Create embedded video with autoplay (muted for autoplay to work)
                mediaItemDiv.className += ' media-item-video';
                
                const iframe = document.createElement('iframe');
                iframe.src = `https://www.youtube.com/embed/${mediaItem.videoId}?autoplay=1&mute=1&loop=1&playlist=${mediaItem.videoId}&controls=0`;
                iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
                iframe.allowFullscreen = true;
                iframe.title = `${game.Title || game.game_name || game.title} - Trailer`;
                
                // Add overlay icon to indicate it's clickable for fullscreen
                const overlay = document.createElement('div');
                overlay.className = 'video-overlay';
                const overlayIcon = document.createElement('div');
                overlayIcon.className = 'video-overlay-icon';
                overlay.appendChild(overlayIcon);
                
                mediaItemDiv.appendChild(iframe);
                mediaItemDiv.appendChild(overlay);
                
                // Click to enlarge
                mediaItemDiv.addEventListener('click', () => openMediaModal(index, mediaItems));
            } else {
                // Image
                const img = document.createElement('img');
                img.src = mediaItem.src;
                img.alt = `${game.Title || game.game_name || game.title} - Screenshot ${mediaItem.screenshotNumber}`;
                img.loading = 'lazy';
                
                mediaItemDiv.appendChild(img);
                
                // Click to enlarge and enable swiping
                mediaItemDiv.addEventListener('click', () => openMediaModal(index, mediaItems));
            }
            
            mediaGallery.appendChild(mediaItemDiv);
        });
        
        mediaSection.style.display = 'block';
    } else {
        mediaSection.style.display = 'none';
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
    modalNavPrev.addEventListener('click', showPreviousMedia);
    modalNavNext.addEventListener('click', showNextMedia);
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
        // Arrow keys for navigation in modal
        if (mediaModal.classList.contains('active')) {
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                showPreviousMedia();
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                showNextMedia();
            }
        }
    });
    
    // Touch support for swipe gestures in modal
    let touchStartX = 0;
    let touchEndX = 0;
    
    mediaModal.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    mediaModal.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold) {
            // Swipe left - next
            showNextMedia();
        }
        if (touchEndX > touchStartX + swipeThreshold) {
            // Swipe right - previous
            showPreviousMedia();
        }
    }
}

// Open media in modal with navigation
function openMediaModal(index, mediaItems) {
    currentMediaItems = mediaItems;
    currentMediaIndex = index;
    showMediaAtIndex(currentMediaIndex);
    mediaModal.classList.add('active');
    updateNavigationButtons();
}

// Show media at specific index
function showMediaAtIndex(index) {
    const mediaItem = currentMediaItems[index];
    
    if (mediaItem.type === 'video') {
        modalImage.style.display = 'none';
        modalVideo.style.display = 'block';
        
        // Create YouTube embed iframe with autoplay and sound enabled for modal
        const iframe = document.createElement('iframe');
        iframe.src = `https://www.youtube.com/embed/${mediaItem.videoId}?autoplay=1`;
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        iframe.allowFullscreen = true;
        
        modalVideo.innerHTML = '';
        modalVideo.appendChild(iframe);
    } else {
        modalVideo.style.display = 'none';
        modalVideo.innerHTML = '';
        modalImage.src = mediaItem.src;
        modalImage.style.display = 'block';
    }
}

// Show previous media
function showPreviousMedia() {
    if (currentMediaItems.length === 0) return;
    
    currentMediaIndex--;
    if (currentMediaIndex < 0) {
        currentMediaIndex = currentMediaItems.length - 1;
    }
    showMediaAtIndex(currentMediaIndex);
    updateNavigationButtons();
}

// Show next media
function showNextMedia() {
    if (currentMediaItems.length === 0) return;
    
    currentMediaIndex++;
    if (currentMediaIndex >= currentMediaItems.length) {
        currentMediaIndex = 0;
    }
    showMediaAtIndex(currentMediaIndex);
    updateNavigationButtons();
}

// Update navigation button visibility
function updateNavigationButtons() {
    if (currentMediaItems.length > 1) {
        modalNavPrev.classList.add('visible');
        modalNavNext.classList.add('visible');
    } else {
        modalNavPrev.classList.remove('visible');
        modalNavNext.classList.remove('visible');
    }
}

// Open image in modal (legacy support)
function openImageModal(imageSrc) {
    currentMediaItems = [{ type: 'image', src: imageSrc, index: 0 }];
    currentMediaIndex = 0;
    showMediaAtIndex(currentMediaIndex);
    mediaModal.classList.add('active');
    updateNavigationButtons();
}

// Open video in modal (legacy support)
function openVideoModal(videoId) {
    currentMediaItems = [{ type: 'video', videoId: videoId, index: 0 }];
    currentMediaIndex = 0;
    showMediaAtIndex(currentMediaIndex);
    mediaModal.classList.add('active');
    updateNavigationButtons();
}

// Close modal
function closeModal() {
    mediaModal.classList.remove('active');
    modalImage.src = '';
    modalImage.style.display = 'none';
    modalVideo.style.display = 'none';
    modalVideo.innerHTML = '';
    currentMediaItems = [];
    currentMediaIndex = 0;
    modalNavPrev.classList.remove('visible');
    modalNavNext.classList.remove('visible');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
