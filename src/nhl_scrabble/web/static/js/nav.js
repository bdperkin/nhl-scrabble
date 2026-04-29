/**
 * NHL Scrabble Analyzer - Mobile Navigation
 * Responsive hamburger menu for mobile devices
 */

/**
 * MobileNav - Handles responsive mobile navigation menu.
 *
 * Features:
 * - Hamburger menu toggle
 * - Close on outside click
 * - Close on link click
 * - Keyboard accessibility
 * - Smooth animations
 */
class MobileNav {
    /**
     * Create mobile navigation controller.
     *
     * @param {Object} options - Configuration options
     * @param {string} [options.toggleId='navToggle'] - Toggle button ID
     * @param {string} [options.menuId='navMenu'] - Menu container ID
     * @param {string} [options.openClass='open'] - Class added when menu is open
     */
    constructor(options = {}) {
        this.options = {
            toggleId: 'navToggle',
            menuId: 'navMenu',
            openClass: 'open',
            ...options
        };

        this.navToggle = document.getElementById(this.options.toggleId);
        this.navMenu = document.getElementById(this.options.menuId);
        this.body = document.body;

        if (!this.navToggle || !this.navMenu) {
            console.warn('Mobile nav elements not found');
            return;
        }

        this.isOpen = false;
        this.init();
    }

    /**
     * Initialize mobile navigation.
     * Sets up event listeners.
     */
    init() {
        // Toggle button click
        this.navToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (this.isOpen &&
                !this.navToggle.contains(e.target) &&
                !this.navMenu.contains(e.target)) {
                this.close();
            }
        });

        // Close on menu link click
        this.navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                this.close();
            });
        });

        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
                this.navToggle.focus();
            }
        });

        // Set up ARIA attributes
        this.navToggle.setAttribute('aria-expanded', 'false');
        this.navToggle.setAttribute('aria-controls', this.options.menuId);
        this.navMenu.setAttribute('aria-hidden', 'true');

        // Make links unfocusable when menu is hidden
        this.setLinksTabindex('-1');
    }

    /**
     * Toggle menu open/closed.
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Open the menu.
     */
    open() {
        this.navMenu.classList.add(this.options.openClass);
        this.navToggle.classList.add(this.options.openClass);
        this.body.classList.add('nav-open');
        this.isOpen = true;

        // Update ARIA attributes
        this.navToggle.setAttribute('aria-expanded', 'true');
        this.navMenu.setAttribute('aria-hidden', 'false');

        // Make links focusable when menu is open
        this.setLinksTabindex('0');

        // Trap focus in menu
        this.trapFocus();
    }

    /**
     * Close the menu.
     */
    close() {
        this.navMenu.classList.remove(this.options.openClass);
        this.navToggle.classList.remove(this.options.openClass);
        this.body.classList.remove('nav-open');
        this.isOpen = false;

        // Update ARIA attributes
        this.navToggle.setAttribute('aria-expanded', 'false');
        this.navMenu.setAttribute('aria-hidden', 'true');

        // Make links unfocusable when menu is hidden
        this.setLinksTabindex('-1');

        // Release focus trap
        this.releaseFocus();
    }

    /**
     * Set tabindex on all links in the menu.
     * Prevents keyboard focus on hidden menu links.
     *
     * @param {string} value - Tabindex value ('0' or '-1')
     */
    setLinksTabindex(value) {
        const links = this.navMenu.querySelectorAll('a');
        links.forEach(link => {
            if (value === '-1') {
                link.setAttribute('tabindex', '-1');
            } else {
                link.removeAttribute('tabindex');
            }
        });
    }

    /**
     * Trap focus within menu when open.
     * Ensures keyboard navigation stays within menu.
     */
    trapFocus() {
        const focusableElements = this.navMenu.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        this.focusTrapHandler = (e) => {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                // Shift+Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };

        document.addEventListener('keydown', this.focusTrapHandler);

        // Focus first element
        firstElement.focus();
    }

    /**
     * Release focus trap.
     */
    releaseFocus() {
        if (this.focusTrapHandler) {
            document.removeEventListener('keydown', this.focusTrapHandler);
            this.focusTrapHandler = null;
        }
    }
}

/**
 * Create hamburger button HTML.
 * Returns HTML string for hamburger icon.
 *
 * @returns {string} HTML string
 */
function createHamburgerHTML() {
    return `
        <span class="hamburger">
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
        </span>
    `;
}

/**
 * Initialize mobile navigation on page load.
 */
function initializeMobileNav() {
    // Check if mobile nav elements exist
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        new MobileNav();
    }
}

// Auto-initialize on DOMContentLoaded
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeMobileNav);
    } else {
        initializeMobileNav();
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        MobileNav,
        createHamburgerHTML,
        initializeMobileNav
    };
}
