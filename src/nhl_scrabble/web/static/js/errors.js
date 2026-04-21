/**
 * NHL Scrabble Analyzer - Error Handling
 * Toast notifications and error message handling
 */

/**
 * ErrorHandler - Manages error display and user notifications.
 *
 * Features:
 * - Toast notifications (error, warning, success, info)
 * - Auto-dismiss timers
 * - Manual close buttons
 * - Accessible announcements
 */
class ErrorHandler {
    /**
     * Show toast notification.
     *
     * @param {string} message - Message to display
     * @param {string} [type='error'] - Toast type (error, warning, success, info)
     * @param {number} [duration=5000] - Auto-dismiss duration in ms (0 = no auto-dismiss)
     * @returns {HTMLElement} Toast element
     */
    static show(message, type = 'error', duration = 5000) {
        const toast = this.createToast(message, type);
        document.body.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Auto-dismiss if duration > 0
        if (duration > 0) {
            setTimeout(() => {
                this.dismissToast(toast);
            }, duration);
        }

        return toast;
    }

    /**
     * Show error toast.
     *
     * @param {string} message - Error message
     * @param {number} [duration=5000] - Auto-dismiss duration
     * @returns {HTMLElement} Toast element
     */
    static error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    /**
     * Show warning toast.
     *
     * @param {string} message - Warning message
     * @param {number} [duration=5000] - Auto-dismiss duration
     * @returns {HTMLElement} Toast element
     */
    static warning(message, duration = 5000) {
        return this.show(message, 'warning', duration);
    }

    /**
     * Show success toast.
     *
     * @param {string} message - Success message
     * @param {number} [duration=4000] - Auto-dismiss duration
     * @returns {HTMLElement} Toast element
     */
    static success(message, duration = 4000) {
        return this.show(message, 'success', duration);
    }

    /**
     * Show info toast.
     *
     * @param {string} message - Info message
     * @param {number} [duration=4000] - Auto-dismiss duration
     * @returns {HTMLElement} Toast element
     */
    static info(message, duration = 4000) {
        return this.show(message, 'info', duration);
    }

    /**
     * Create toast element.
     *
     * @param {string} message - Message text
     * @param {string} type - Toast type
     * @returns {HTMLElement} Toast element
     */
    static createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');

        const icon = this.getIcon(type);
        const sanitizedMessage = this.sanitizeHTML(message);

        toast.innerHTML = `
            <span class="toast-icon" aria-hidden="true">${icon}</span>
            <span class="toast-message">${sanitizedMessage}</span>
            <button class="toast-close" aria-label="Close notification">×</button>
        `;

        // Close button handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            this.dismissToast(toast);
        });

        return toast;
    }

    /**
     * Dismiss toast notification.
     *
     * @param {HTMLElement} toast - Toast element to dismiss
     */
    static dismissToast(toast) {
        toast.classList.add('fade-out');
        toast.classList.remove('show');

        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    }

    /**
     * Get icon for toast type.
     *
     * @param {string} type - Toast type
     * @returns {string} Icon emoji
     */
    static getIcon(type) {
        const icons = {
            error: '❌',
            warning: '⚠️',
            success: '✅',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    /**
     * Sanitize HTML to prevent XSS.
     * Basic escaping for user-generated content.
     *
     * @param {string} html - HTML string to sanitize
     * @returns {string} Sanitized string
     */
    static sanitizeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    /**
     * Handle API error.
     * Extracts error message and shows appropriate toast.
     *
     * @param {Error|Response|Object} error - Error object
     */
    static handleApiError(error) {
        console.error('API Error:', error);

        let message = 'An error occurred. Please try again.';

        // Handle fetch Response error
        if (error instanceof Response) {
            message = `Error ${error.status}: ${error.statusText}`;
        }
        // Handle Error object
        else if (error instanceof Error) {
            message = error.message;
        }
        // Handle error object with response
        else if (error.response) {
            if (error.response.status) {
                message = `Error ${error.response.status}: ${error.response.statusText || 'Request failed'}`;
            }
            // Try to extract error message from response body
            if (error.response.data && error.response.data.detail) {
                message = error.response.data.detail;
            } else if (error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
        }
        // Handle string error
        else if (typeof error === 'string') {
            message = error;
        }
        // Handle object with message property
        else if (error.message) {
            message = error.message;
        }

        this.error(message);
    }

    /**
     * Handle network error.
     * Shows specific message for offline/network issues.
     */
    static handleNetworkError() {
        this.error(
            'Network error. Please check your internet connection and try again.',
            0 // Don't auto-dismiss
        );
    }

    /**
     * Clear all toast notifications.
     */
    static clearAll() {
        document.querySelectorAll('.toast').forEach(toast => {
            this.dismissToast(toast);
        });
    }
}

/**
 * Initialize global error handlers.
 * Catches unhandled promise rejections and errors.
 */
function initializeErrorHandlers() {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', event => {
        console.error('Unhandled promise rejection:', event.reason);

        // Check if it's a fetch error
        if (event.reason instanceof TypeError && event.reason.message.includes('fetch')) {
            ErrorHandler.handleNetworkError();
        } else {
            ErrorHandler.handleApiError(event.reason);
        }

        // Prevent default browser error handling
        event.preventDefault();
    });

    // Handle global errors (optional - for debugging)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.addEventListener('error', event => {
            console.error('Global error:', event.error);
        });
    }
}

/**
 * Create loading state wrapper for async operations.
 * Shows loading toast while operation is in progress.
 *
 * @param {Function} asyncFunc - Async function to wrap
 * @param {string} [loadingMessage='Loading...'] - Loading message
 * @returns {Function} Wrapped function
 */
function withLoadingState(asyncFunc, loadingMessage = 'Loading...') {
    return async function(...args) {
        const loadingToast = ErrorHandler.info(loadingMessage, 0);

        try {
            const result = await asyncFunc.apply(this, args);
            ErrorHandler.dismissToast(loadingToast);
            return result;
        } catch (error) {
            ErrorHandler.dismissToast(loadingToast);
            ErrorHandler.handleApiError(error);
            throw error;
        }
    };
}

/**
 * Retry failed operation with exponential backoff.
 *
 * @param {Function} asyncFunc - Async function to retry
 * @param {number} [maxRetries=3] - Maximum retry attempts
 * @param {number} [baseDelay=1000] - Base delay in ms
 * @returns {Promise<any>} Result of async function
 */
async function retryWithBackoff(asyncFunc, maxRetries = 3, baseDelay = 1000) {
    let lastError;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await asyncFunc();
        } catch (error) {
            lastError = error;

            if (attempt < maxRetries - 1) {
                const delay = baseDelay * Math.pow(2, attempt);
                console.log(`Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    throw lastError;
}

// Auto-initialize on DOMContentLoaded
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeErrorHandlers);
    } else {
        initializeErrorHandlers();
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ErrorHandler,
        initializeErrorHandlers,
        withLoadingState,
        retryWithBackoff
    };
}
