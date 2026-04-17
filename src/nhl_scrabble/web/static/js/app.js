/**
 * NHL Scrabble Analyzer - Frontend JavaScript
 * Handles form submission, API calls, and result display
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const resultsContainer = document.getElementById('results');
    const errorContainer = document.getElementById('error');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    /**
     * Handle form submission
     * @param {Event} event - Form submit event
     */
    async function handleFormSubmit(event) {
        event.preventDefault();

        // Get form data
        const topPlayers = document.getElementById('topPlayers').value;
        const topTeamPlayers = document.getElementById('topTeamPlayers').value;
        const useCache = document.getElementById('useCache').checked;

        // Show loading state
        setLoadingState(true);
        hideError();
        hideResults();

        try {
            // Call API
            const response = await fetch(`/api/analyze?top_players=${topPlayers}&top_team_players=${topTeamPlayers}&use_cache=${useCache}`);

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            // Display results
            displayResults(data);

        } catch (error) {
            console.error('Analysis failed:', error);
            showError(`Failed to fetch analysis: ${error.message}`);
        } finally {
            setLoadingState(false);
        }
    }

    /**
     * Set loading state for the analyze button
     * @param {boolean} isLoading - Whether the button is in loading state
     */
    function setLoadingState(isLoading) {
        const btnText = analyzeBtn.querySelector('.btn-text');
        const btnLoading = analyzeBtn.querySelector('.btn-loading');

        if (isLoading) {
            btnText.hidden = true;
            btnLoading.hidden = false;
            analyzeBtn.disabled = true;
        } else {
            btnText.hidden = false;
            btnLoading.hidden = true;
            analyzeBtn.disabled = false;
        }
    }

    /**
     * Display results in the results container
     * @param {Object} data - Analysis results data
     */
    function displayResults(data) {
        // For now, just display JSON (will be enhanced in next task with proper formatting)
        resultsContainer.innerHTML = `
            <div class="results-section">
                <h3>Analysis Results</h3>
                <p class="success-message">✅ Analysis completed successfully!</p>
                <details>
                    <summary style="cursor: pointer; padding: 10px; background: var(--color-light); border-radius: 8px; margin: 10px 0;">
                        <strong>View Results (JSON)</strong>
                    </summary>
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 8px; overflow-x: auto; margin-top: 10px;">${JSON.stringify(data, null, 2)}</pre>
                </details>
                <p style="margin-top: 20px; color: #666;">
                    <em>Note: Pretty formatted results with tables and charts will be added in the next task (005-interactive-javascript).</em>
                </p>
            </div>
        `;
        resultsContainer.hidden = false;

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    function showError(message) {
        errorContainer.innerHTML = `
            <strong>Error:</strong> ${message}
        `;
        errorContainer.hidden = false;
    }

    /**
     * Hide error message
     */
    function hideError() {
        errorContainer.hidden = true;
        errorContainer.innerHTML = '';
    }

    /**
     * Hide results
     */
    function hideResults() {
        resultsContainer.hidden = true;
        resultsContainer.innerHTML = '';
    }
});
