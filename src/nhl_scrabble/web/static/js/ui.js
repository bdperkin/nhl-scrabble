/**
 * NHL Scrabble Analyzer - UI Interactions
 * Smooth scrolling, animations, and general UX enhancements
 */

/**
 * Initialize smooth scrolling for anchor links.
 * Enables smooth scroll behavior for all hash links.
 */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Ignore empty hashes
            if (href === '#') return;

            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();

                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Update URL without jumping
                if (history.pushState) {
                    history.pushState(null, null, href);
                }

                // Focus target for accessibility
                target.setAttribute('tabindex', '-1');
                target.focus({ preventScroll: true });
            }
        });
    });
}

/**
 * Initialize fade-in animations on scroll.
 * Uses Intersection Observer API for performance.
 */
function initScrollAnimations() {
    // Check for browser support
    if (!('IntersectionObserver' in window)) {
        console.warn('IntersectionObserver not supported, skipping scroll animations');
        return;
    }

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                fadeInObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all elements with fade-on-scroll class
    document.querySelectorAll('.fade-on-scroll').forEach(el => {
        fadeInObserver.observe(el);
    });
}

/**
 * Initialize loading overlay functionality.
 * Shows/hides global loading indicator.
 */
class LoadingOverlay {
    constructor(overlayId = 'loadingOverlay') {
        this.overlay = document.getElementById(overlayId);
        if (!this.overlay) {
            this.createOverlay(overlayId);
        }
    }

    /**
     * Create loading overlay if it doesn't exist.
     *
     * @param {string} overlayId - Overlay element ID
     */
    createOverlay(overlayId) {
        this.overlay = document.createElement('div');
        this.overlay.id = overlayId;
        this.overlay.className = 'loading-overlay';
        this.overlay.setAttribute('role', 'status');
        this.overlay.setAttribute('aria-live', 'polite');
        this.overlay.setAttribute('aria-label', 'Loading');
        this.overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner-large"></div>
                <p>Loading NHL data...</p>
            </div>
        `;
        this.overlay.hidden = true;
        document.body.appendChild(this.overlay);
    }

    /**
     * Show loading overlay.
     *
     * @param {string} [message] - Optional loading message
     */
    show(message = 'Loading NHL data...') {
        if (!this.overlay) return;

        const messageEl = this.overlay.querySelector('p');
        if (messageEl) {
            messageEl.textContent = message;
        }

        this.overlay.hidden = false;
        this.overlay.classList.add('active');
        document.body.classList.add('loading');
    }

    /**
     * Hide loading overlay.
     */
    hide() {
        if (!this.overlay) return;

        this.overlay.classList.remove('active');
        // Delay hiding to allow fade-out animation
        setTimeout(() => {
            this.overlay.hidden = true;
            document.body.classList.remove('loading');
        }, 300);
    }

    /**
     * Check if overlay is currently shown.
     *
     * @returns {boolean} True if overlay is visible
     */
    isVisible() {
        return this.overlay && !this.overlay.hidden;
    }
}

/**
 * Debounce function for performance optimization.
 * Limits how often a function can be called.
 *
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function for performance optimization.
 * Ensures function is called at most once per interval.
 *
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Add pulse animation to element.
 * Useful for highlighting updates.
 *
 * @param {HTMLElement|string} elementOrId - Element or element ID
 * @param {number} [duration=600] - Animation duration in ms
 */
function pulseElement(elementOrId, duration = 600) {
    const element = typeof elementOrId === 'string'
        ? document.getElementById(elementOrId)
        : elementOrId;

    if (!element) return;

    element.classList.add('pulse');
    setTimeout(() => {
        element.classList.remove('pulse');
    }, duration);
}

/**
 * Scroll to top button functionality.
 * Shows button when user scrolls down, hides when at top.
 */
function initScrollToTop() {
    const scrollBtn = document.getElementById('scrollToTop');
    if (!scrollBtn) return;

    // Show/hide button based on scroll position
    const toggleScrollBtn = throttle(() => {
        if (window.pageYOffset > 300) {
            scrollBtn.classList.add('visible');
        } else {
            scrollBtn.classList.remove('visible');
        }
    }, 200);

    window.addEventListener('scroll', toggleScrollBtn);

    // Scroll to top on click
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Copy text to clipboard.
 *
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
async function copyToClipboard(text) {
    try {
        if (navigator.clipboard) {
            await navigator.clipboard.writeText(text);
            return true;
        } else {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            const success = document.execCommand('copy');
            document.body.removeChild(textarea);
            return success;
        }
    } catch (err) {
        console.error('Failed to copy to clipboard:', err);
        return false;
    }
}

/**
 * Initialize all UI enhancements.
 * Call this on page load.
 */
function initializeUI() {
    initSmoothScrolling();
    initScrollAnimations();
    initScrollToTop();

    // Add copy-to-clipboard for code blocks
    document.querySelectorAll('pre[data-copyable]').forEach(pre => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.textContent = 'Copy';
        copyBtn.setAttribute('aria-label', 'Copy code to clipboard');

        copyBtn.addEventListener('click', async () => {
            const code = pre.textContent;
            const success = await copyToClipboard(code);
            if (success) {
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                }, 2000);
            }
        });

        pre.style.position = 'relative';
        pre.appendChild(copyBtn);
    });
}

// Create global loading overlay instance
let globalLoadingOverlay;

/**
 * Get global loading overlay instance.
 *
 * @returns {LoadingOverlay} Global loading overlay
 */
function getLoadingOverlay() {
    if (!globalLoadingOverlay) {
        globalLoadingOverlay = new LoadingOverlay();
    }
    return globalLoadingOverlay;
}

// Auto-initialize on DOMContentLoaded
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeUI);
    } else {
        initializeUI();
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initSmoothScrolling,
        initScrollAnimations,
        initScrollToTop,
        LoadingOverlay,
        debounce,
        throttle,
        pulseElement,
        copyToClipboard,
        initializeUI,
        getLoadingOverlay
    };
}
