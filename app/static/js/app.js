/**
 * Masonry & HTMX Integration
 * Handles Masonry grid initialization, HTMX event listeners, filtering, and modal
 */

let msnry; // Global Masonry instance
let allPosts = []; // Store all posts for filtering (future use)
// Composite filter state
let activeMedium = 'all';
let searchQuery = '';
// Multi-select sets for evaluation and rating scores
let selectedEvaluationScores = new Set();
let selectedRatingScores = new Set();

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
    
    // Initialize medium filters
    initFilters();
    // Initialize score dropdown filters
    initScoreDropdown();
    
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
                // Recompute score counts after new items
                updateScoreCounts();
                updateScoreButtonStates();
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
            
            activeMedium = this.dataset.filter;
            applyCompositeFilters();
        });
    });
}

/**
 * Handle search input
 */
function handleSearch(query) {
    searchQuery = query.toLowerCase();
    applyCompositeFilters();
}

/**
 * Filter posts by medium type
 */
// (Deprecated) filterPosts replaced by composite filtering

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
                searchQuery = this.value.toLowerCase();
                applyCompositeFilters();
            }, 300);
        });
    }
}

/**
 * Search posts by title and tags
 */
// Composite filtering: medium + search + evaluation + rating
function applyCompositeFilters() {
    const gridItems = document.querySelectorAll('.grid-item');
    gridItems.forEach(item => {
        if (item.classList.contains('year-separator')) return; // skip dividers
        const card = item.querySelector('.card');
        if (!card) return;
        const itemMedium = item.dataset.medium;
        const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
        const tags = Array.from(card.querySelectorAll('.tag')).map(t => t.textContent.toLowerCase());
        const evalNum = parseInt(card.getAttribute('data-evaluation-num') || '0');
        const ratingNum = parseInt(card.getAttribute('data-rating-num') || '0');

        const mediumOk = activeMedium === 'all' || itemMedium === activeMedium;
        const searchOk = !searchQuery || title.includes(searchQuery) || tags.some(tag => tag.includes(searchQuery));
        const evalOk = selectedEvaluationScores.size === 0 || selectedEvaluationScores.has(evalNum);
        const ratingOk = selectedRatingScores.size === 0 || selectedRatingScores.has(ratingNum);

        if (mediumOk && searchOk && evalOk && ratingOk) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
    setTimeout(() => { if (msnry) msnry.layout(); }, 100);
}

// Score Dropdown Initialization
function initScoreDropdown() {
    updateScoreCounts();
    attachScoreDropdownHandlers();
    updateScoreButtonStates();
}

function attachScoreDropdownHandlers() {
    const evalItems = document.querySelectorAll('#evaluation-score-items .score-item-btn');
    const ratingItems = document.querySelectorAll('#rating-score-items .score-item-btn');
    evalItems.forEach(btn => {
        btn.addEventListener('click', () => {
            const val = parseInt(btn.getAttribute('data-value'));
            if (selectedEvaluationScores.has(val)) {
                selectedEvaluationScores.delete(val);
            } else {
                selectedEvaluationScores.add(val);
            }
            updateScoreButtonStates();
            applyCompositeFilters();
        });
    });
    ratingItems.forEach(btn => {
        btn.addEventListener('click', () => {
            const val = parseInt(btn.getAttribute('data-value'));
            if (selectedRatingScores.has(val)) {
                selectedRatingScores.delete(val);
            } else {
                selectedRatingScores.add(val);
            }
            updateScoreButtonStates();
            applyCompositeFilters();
        });
    });
    const clearBtns = document.querySelectorAll('.score-clear-btn');
    clearBtns.forEach(clear => {
        clear.addEventListener('click', () => {
            const type = clear.getAttribute('data-clear');
            if (type === 'evaluation') selectedEvaluationScores.clear();
            if (type === 'rating') selectedRatingScores.clear();
            updateScoreButtonStates();
            applyCompositeFilters();
        });
    });
}

function updateScoreCounts() {
    const counts = {
        evaluation: {1:0,2:0,3:0,4:0,5:0},
        rating: {1:0,2:0,3:0,4:0,5:0}
    };
    document.querySelectorAll('.grid-item').forEach(item => {
        if (item.classList.contains('year-separator')) return;
        const card = item.querySelector('.card');
        if (!card) return;
        const evalNum = parseInt(card.getAttribute('data-evaluation-num') || '0');
        const ratingNum = parseInt(card.getAttribute('data-rating-num') || '0');
        if (evalNum >=1 && evalNum <=5) counts.evaluation[evalNum] += 1;
        if (ratingNum >=1 && ratingNum <=5) counts.rating[ratingNum] += 1;
    });
    // Update DOM
    Object.keys(counts.evaluation).forEach(k => {
        const span = document.querySelector(`[data-count-for='evaluation-${k}']`);
        if (span) span.textContent = `(${counts.evaluation[k]})`;
    });
    Object.keys(counts.rating).forEach(k => {
        const span = document.querySelector(`[data-count-for='rating-${k}']`);
        if (span) span.textContent = `(${counts.rating[k]})`;
    });
}

function updateScoreButtonStates() {
    document.querySelectorAll('#evaluation-score-items .score-item-btn').forEach(btn => {
        const val = parseInt(btn.getAttribute('data-value'));
        if (selectedEvaluationScores.has(val)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    document.querySelectorAll('#rating-score-items .score-item-btn').forEach(btn => {
        const val = parseInt(btn.getAttribute('data-value'));
        if (selectedRatingScores.has(val)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
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
    let evaluationNum = parseInt(card.getAttribute('data-evaluation-num') || '0');
    let ratingNum = parseInt(card.getAttribute('data-rating-num') || '0');
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
    // Evaluation & Rating Controls
    footer += '<div class="modal-rating-evaluation">';
    footer += renderStarGroup('evaluation', evaluationNum, postId);
    footer += renderStarGroup('rating', ratingNum, postId);
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
    // Attach star listeners after modal renders
    setTimeout(initStarHandlers, 50);
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

function renderStarGroup(type, currentValue, postId) {
    const label = type === 'evaluation' ? 'Your Evaluation' : 'Audience Rating';
    let html = `<div class="star-group" data-type="${type}" data-post-id="${postId}">`;
    html += `<div class="star-group-label">${label}:</div>`;
    for (let i = 1; i <= 5; i++) {
        const filled = i <= currentValue;
        html += `<button class="star-btn" type="button" data-value="${i}" aria-label="${label} ${i} star" title="${label} ${i} star">` +
            `<i class="fa-${filled ? 'solid' : 'regular'} fa-star"></i>` +
            '</button>';
    }
    html += '</div>';
    return html;
}

function initStarHandlers() {
    document.querySelectorAll('.star-group').forEach(group => {
        const type = group.getAttribute('data-type');
        const postId = group.getAttribute('data-post-id');
        group.querySelectorAll('.star-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const value = parseInt(btn.getAttribute('data-value'));
                submitStarValue(type, postId, value, group);
            });
        });
    });
}

function submitStarValue(type, postId, value, groupEl) {
    const endpoint = `/api/post/${postId}/${type === 'evaluation' ? 'evaluation' : 'rating'}`;
    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value })
    }).then(r => r.json())
      .then(json => {
          if (json.error) {
              console.error('Rating update error', json.error);
              return;
          }
          // Update stars visual
          groupEl.querySelectorAll('.star-btn').forEach(btn => {
              const v = parseInt(btn.getAttribute('data-value'));
              const icon = btn.querySelector('i');
              if (v <= value) {
                  icon.classList.remove('fa-regular');
                  icon.classList.add('fa-solid');
              } else {
                  icon.classList.remove('fa-solid');
                  icon.classList.add('fa-regular');
              }
          });
      })
      .catch(err => console.error('Rating update fetch failed', err));
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
