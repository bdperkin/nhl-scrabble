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
            // Call API to get both HTML and JSON
            const response = await fetch(`/api/analyze?top_players=${topPlayers}&top_team_players=${topTeamPlayers}&use_cache=${useCache}`, {
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            // Fetch HTML version for display
            const htmlResponse = await fetch(`/api/analyze?top_players=${topPlayers}&top_team_players=${topTeamPlayers}&use_cache=${useCache}`, {
                headers: {
                    'HX-Request': 'true',
                    'Accept': 'text/html'
                }
            });

            if (htmlResponse.ok) {
                const html = await htmlResponse.text();
                resultsContainer.innerHTML = html;
            }

            // Display results (initialize interactive features)
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
        // The actual HTML will be rendered server-side
        // This function now handles initialization of interactive features
        resultsContainer.hidden = false;

        // Initialize interactive features after content is loaded
        setTimeout(() => {
            initializeCharts(data);
            initializeExportButtons();
            initializeTableSorting();

            // Re-initialize scroll animations for dynamically loaded content
            if (typeof initScrollAnimations === 'function') {
                initScrollAnimations();
            }
        }, 100);

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * Initialize Chart.js visualizations
     * @param {Object} data - Analysis results data
     */
    function initializeCharts(data) {
        // Check if chart functions are available
        if (typeof createTeamScoresChart === 'undefined' || typeof createPlayerDistributionChart === 'undefined') {
            console.warn('Chart functions not loaded');
            return;
        }

        // Extract team and player data for charts
        const teams = data.team_standings || [];
        const players = data.top_players || [];

        // Create team scores chart
        if (teams.length > 0) {
            createTeamScoresChart(teams);
        }

        // Create player distribution chart
        if (players.length > 0) {
            createPlayerDistributionChart(players);
        }
    }

    /**
     * Initialize export buttons for tables
     */
    function initializeExportButtons() {
        // Setup export for players table
        const playersTable = document.getElementById('playersTable');
        if (playersTable) {
            setupTableExport('playersTable', 'nhl-scrabble-players', {
                csvButtonId: 'export-playersTable-csv',
                jsonButtonId: 'export-playersTable-json'
            });
        }

        // Setup export for teams table
        const teamsTable = document.getElementById('teamsTable');
        if (teamsTable) {
            setupTableExport('teamsTable', 'nhl-scrabble-teams', {
                csvButtonId: 'export-teamsTable-csv',
                jsonButtonId: 'export-teamsTable-json'
            });
        }
    }

    /**
     * Initialize table sorting
     */
    function initializeTableSorting() {
        // Tables with class 'sortable' are auto-initialized
        // But we can also manually initialize specific tables
        if (document.getElementById('playersTable')) {
            new TableSort('playersTable');
        }
        if (document.getElementById('teamsTable')) {
            new TableSort('teamsTable');
        }
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
