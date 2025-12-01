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

    // Initialize client-side flip debug logging
    initFlipDebugLogging();
    
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
    // Find the grid-item for this post
    const gridItem = document.querySelector(`.grid-item[data-post-id='${postId}']`);
    if (!gridItem) return;
    const card = gridItem.querySelector('.card');
    if (!card) return;
    // Extract data from card
    const title = card.querySelector('.card-title')?.textContent || '';
    // Try to get content from a data attribute or fallback (for now, show placeholder)
    // In a real app, you might fetch the clean content via AJAX or store it in a data-content attribute
    let content = card.getAttribute('data-content') || '';
    if (!content) {
        // Fallback: show a placeholder
        content = '[Content not loaded. Implement AJAX fetch or data-content attribute.]';
    }
    // Get date and location from card-meta or data attributes
    let date = card.getAttribute('data-date') || '';
    let location = card.getAttribute('data-location') || '';
    let medium = card.getAttribute('data-medium') || '';
    let subcategory = card.getAttribute('data-subcategory') || '';
    // Build modal footer HTML (two rows, two columns)
    // Format date as 'Month D, YYYY'
    let formattedDate = '';
    if (date) {
        const dateObj = new Date(date);
        if (!isNaN(dateObj)) {
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            formattedDate = dateObj.toLocaleDateString('en-US', options);
        } else {
            formattedDate = date;
        }
    }
    let mediumPill = '';
    if (medium) {
        mediumPill = `<span class="modal-footer-pill modal-footer-medium-pill modal-footer-pill-${medium.toLowerCase()}">${medium}</span>`;
    }
    let subcategoryPill = '';
    if (subcategory) {
        subcategoryPill = `<span class="modal-footer-pill modal-footer-subcategory-pill modal-footer-pill-${subcategory.toLowerCase()}">${subcategory}</span>`;
    }
    let footer = '';
    footer += '<div class="modal-footer-grid">';
    footer += '  <div class="modal-footer-col modal-footer-col-left">';
    footer += `    <div class="modal-footer-row modal-footer-date"><em>${formattedDate}</em></div>`;
    footer += `    <div class="modal-footer-row modal-footer-location"><em>${location || ''}</em></div>`;
    footer += '  </div>';
    footer += '  <div class="modal-footer-col modal-footer-col-right">';
    footer += '    <div class="modal-footer-row modal-footer-medium">';
    if (mediumPill) footer += mediumPill;
    footer += '    </div>';
    footer += '    <div class="modal-footer-row modal-footer-subcategory">';
    if (subcategoryPill) footer += subcategoryPill;
    footer += '    </div>';
    footer += '  </div>';
    footer += '</div>';

    // Set modal title color based on medium
    showArtwallModal(title, content, footer);
    setTimeout(function() {
        const modalTitle = document.getElementById('artwall-modal-title');
        if (modalTitle) {
            let color = '';
            switch ((medium || '').toLowerCase()) {
                case 'writing':
                    color = getComputedStyle(document.documentElement).getPropertyValue('--theme-writing');
                    break;
                case 'drawing':
                    color = getComputedStyle(document.documentElement).getPropertyValue('--theme-drawing');
                    break;
                case 'audio':
                    color = getComputedStyle(document.documentElement).getPropertyValue('--theme-audio');
                    break;
                case 'sculpture':
                    color = getComputedStyle(document.documentElement).getPropertyValue('--theme-sculpture');
                    break;
                case 'poem':
                    color = getComputedStyle(document.documentElement).getPropertyValue('--theme-poem');
                    break;
                case 'prosepoem':
                    color = getComputedStyle(document.documentElement).getPropertyValue('--theme-prosepoem');
                    break;
                case 'prose':
                    color = getComputedStyle(document.documentElement).getPropertyValue('--theme-prose');
                    break;
                default:
                    color = getComputedStyle(document.documentElement).getPropertyValue('--theme-primary');
            }
            modalTitle.style.color = color || '#1976d2';
        }
    }, 0);
}

function showArtwallModal(title, content, footer) {
    const modal = document.getElementById('artwall-modal');
    if (!modal) return;
    document.getElementById('artwall-modal-title').textContent = title;
    document.getElementById('artwall-modal-body').textContent = content;
    document.getElementById('artwall-modal-footer').innerHTML = footer;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeArtwallModal() {
    const modal = document.getElementById('artwall-modal');
    if (modal) modal.style.display = 'none';
    document.body.style.overflow = '';
}

/**
 * Debug: Send logs to server to inspect flip state from terminal
 */
function initFlipDebugLogging() {
    try {
        const wrappers = document.querySelectorAll('.card-wrapper');
        wrappers.forEach(w => {
            w.addEventListener('mouseenter', () => sendFlipLog(w, 'hover-enter'));
            w.addEventListener('mouseleave', () => sendFlipLog(w, 'hover-leave'));
        });
        // Also log initial state for the first few cards
        wrappers.forEach((w, idx) => { if (idx < 3) sendFlipLog(w, 'initial'); });
    } catch (e) {
        console.error('initFlipDebugLogging error', e);
    }
}

function sendFlipLog(wrapper, eventName) {
    try {
        const card = wrapper.querySelector('.card');
        const front = wrapper.querySelector('.card-front');
        const back = wrapper.querySelector('.card-back');
        if (!card || !front || !back) return;
        const postId = wrapper.closest('.grid-item')?.getAttribute('data-post-id') || null;

        const csCard = getComputedStyle(card);
        const csFront = getComputedStyle(front);
        const csBack = getComputedStyle(back);

        const payload = {
            event: eventName,
            postId: postId,
            cardClasses: card.className,
            frontTextLen: (front.textContent || '').trim().length,
            backTextLen: (back.textContent || '').trim().length,
            cardTransform: csCard.transform,
            cardTransformStyle: csCard.transformStyle,
            frontTransform: csFront.transform,
            backTransform: csBack.transform,
            frontBackface: csFront.backfaceVisibility,
            backBackface: csBack.backfaceVisibility
        };

        fetch('/api/client-log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).catch(() => {});
    } catch (e) {
        console.error('sendFlipLog error', e);
    }
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
