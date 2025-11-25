/**
 * Masonry & HTMX Integration
 * Handles Masonry grid initialization, HTMX event listeners, filtering, and modal
 */

let msnry; // Global Masonry instance
let allPosts = []; // Store all posts for filtering

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Artwall...');
    
    // Get the grid element
    const gridElement = document.querySelector('.grid');
    
    if (!gridElement) {
        console.warn('Grid element not found on this page');
        return;
    }
    
    // Initialize Masonry
    msnry = new Masonry(gridElement, {
        itemSelector: '.grid-item',
        columnWidth: '.grid-sizer',
        gutter: 8,
        fitWidth: false,
        transitionDuration: '0.3s'
    });
    
    console.log('Masonry initialized');
    
    // Wait for all images to load before laying out
    imagesLoaded(gridElement, function() {
        console.log('All images loaded, performing layout');
        msnry.layout();
    });
    
    // Initialize filters
    initFilters();
    
    // Initialize search
    initSearch();
    
    /**
     * HTMX Event Listener: After content is swapped into the DOM
     * This fires when new content is loaded via HTMX (e.g., "Load More")
     */
    document.body.addEventListener('htmx:afterSwap', function(event) {
        console.log('HTMX afterSwap event fired');
        
        // Only process if the swap happened in our grid
        if (event.detail.target.id === 'grid-container') {
            console.log('Processing new grid items...');
            
            // Get all grid items
            const gridItems = event.detail.target.querySelectorAll('.grid-item');
            
            // Wait for images in new items to load
            imagesLoaded(gridItems, function() {
                console.log('Images loaded, reloading Masonry');
                
                // Reload all items
                msnry.reloadItems();
                msnry.layout();
            });
        }
    });
    
    /**
     * HTMX Event Listener: Before request is sent
     */
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        console.log('HTMX request starting...');
    });
    
    /**
     * HTMX Event Listener: After request is complete
     */
    document.body.addEventListener('htmx:afterRequest', function(event) {
        console.log('HTMX request completed');
        
        if (event.detail.failed) {
            console.error('HTMX request failed');
            alert('Failed to load more content. Please try again.');
        }
    });
    
    /**
     * Window resize handler - relayout Masonry
     */
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            console.log('Window resized, re-calculating layout');
            if (msnry) {
                msnry.layout();
            }
        }, 250);
    });
});

/**
 * Initialize filter buttons
 */
function initFilters() {
    const filterBtns = document.querySelectorAll('.icon-btn[data-filter]');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            filterPosts(filter);
        });
    });
}

/**
 * Handle search input
 */
function handleSearch(query) {
    searchPosts(query.toLowerCase());
}

/**
 * Filter posts by medium type
 */
function filterPosts(medium) {
    const gridItems = document.querySelectorAll('.grid-item');
    
    gridItems.forEach(item => {
        // Skip year separators
        if (item.classList.contains('year-separator')) {
            return;
        }
        
        // Use data-medium attribute from grid-item
        const itemMedium = item.dataset.medium;
        
        if (medium === 'all' || itemMedium === medium) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
    
    // Relayout masonry after filtering
    setTimeout(function() {
        if (msnry) {
            msnry.layout();
        }
    }, 100);
}

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        let searchTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                searchPosts(this.value.toLowerCase());
            }, 300);
        });
    }
}

/**
 * Search posts by title and tags
 */
function searchPosts(query) {
    const gridItems = document.querySelectorAll('.grid-item');
    
    gridItems.forEach(item => {
        // Skip year separators
        if (item.classList.contains('year-separator')) {
            return;
        }
        
        const card = item.querySelector('.card');
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const tags = Array.from(card.querySelectorAll('.tag')).map(t => t.textContent.toLowerCase());
        
        const matchesTitle = title.includes(query);
        const matchesTags = tags.some(tag => tag.includes(query));
        
        if (query === '' || matchesTitle || matchesTags) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
    
    // Relayout masonry after search
    setTimeout(function() {
        if (msnry) {
            msnry.layout();
        }
    }, 100);
}

/**
 * Open post in modal or new page
 */
function openPost(postId) {
    console.log('Opening post:', postId);
    // For now, just log. You can implement a modal or navigate to detail page
    // Option 1: Open in modal (requires modal HTML)
    // showPostModal(postId);
    
    // Option 2: Navigate to detail page
    window.location.href = `/post/${postId}`;
}

/**
 * Utility: Smooth scroll to top
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}
