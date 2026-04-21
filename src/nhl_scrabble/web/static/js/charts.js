/**
 * NHL Scrabble Analyzer - Chart Visualizations
 * Chart.js-based visualizations for team scores and player distributions
 */

/**
 * NHL team color scheme for bar charts.
 * Uses official team colors with alpha transparency.
 */
const NHL_TEAM_COLORS = {
    'ANA': 'rgba(252, 76, 2, 0.8)',      // Ducks orange
    'ARI': 'rgba(140, 38, 51, 0.8)',     // Coyotes maroon
    'BOS': 'rgba(252, 181, 20, 0.8)',    // Bruins gold
    'BUF': 'rgba(0, 38, 84, 0.8)',       // Sabres navy
    'CAR': 'rgba(204, 0, 0, 0.8)',       // Hurricanes red
    'CBJ': 'rgba(0, 38, 84, 0.8)',       // Blue Jackets navy
    'CGY': 'rgba(200, 16, 46, 0.8)',     // Flames red
    'CHI': 'rgba(207, 10, 44, 0.8)',     // Blackhawks red
    'COL': 'rgba(111, 38, 61, 0.8)',     // Avalanche burgundy
    'DAL': 'rgba(0, 104, 71, 0.8)',      // Stars green
    'DET': 'rgba(206, 17, 38, 0.8)',     // Red Wings red
    'EDM': 'rgba(4, 30, 66, 0.8)',       // Oilers navy
    'FLA': 'rgba(200, 16, 46, 0.8)',     // Panthers red
    'LAK': 'rgba(17, 17, 17, 0.8)',      // Kings black
    'MIN': 'rgba(2, 73, 48, 0.8)',       // Wild green
    'MTL': 'rgba(175, 30, 45, 0.8)',     // Canadiens red
    'NJD': 'rgba(206, 17, 38, 0.8)',     // Devils red
    'NSH': 'rgba(255, 184, 28, 0.8)',    // Predators gold
    'NYI': 'rgba(0, 83, 155, 0.8)',      // Islanders blue
    'NYR': 'rgba(0, 56, 168, 0.8)',      // Rangers blue
    'OTT': 'rgba(197, 32, 50, 0.8)',     // Senators red
    'PHI': 'rgba(247, 73, 2, 0.8)',      // Flyers orange
    'PIT': 'rgba(252, 181, 20, 0.8)',    // Penguins gold
    'SEA': 'rgba(0, 22, 40, 0.8)',       // Kraken navy
    'SJS': 'rgba(0, 109, 117, 0.8)',     // Sharks teal
    'STL': 'rgba(0, 47, 135, 0.8)',      // Blues blue
    'TBL': 'rgba(0, 40, 104, 0.8)',      // Lightning blue
    'TOR': 'rgba(0, 32, 91, 0.8)',       // Maple Leafs blue
    'UTA': 'rgba(111, 38, 61, 0.8)',     // Utah Hockey Club
    'VAN': 'rgba(0, 32, 91, 0.8)',       // Canucks blue
    'VGK': 'rgba(185, 151, 91, 0.8)',    // Golden Knights gold
    'WPG': 'rgba(4, 30, 66, 0.8)',       // Jets navy
    'WSH': 'rgba(200, 16, 46, 0.8)',     // Capitals red
};

/**
 * Get NHL team color by abbreviation.
 * Falls back to gray if team not found.
 *
 * @param {string} abbrev - Team abbreviation
 * @returns {string} RGBA color string
 */
function getTeamColor(abbrev) {
    return NHL_TEAM_COLORS[abbrev] || 'rgba(100, 100, 100, 0.8)';
}

/**
 * Get border color (full opacity version of fill color).
 *
 * @param {string} abbrev - Team abbreviation
 * @returns {string} RGBA color string with full opacity
 */
function getTeamBorderColor(abbrev) {
    const color = getTeamColor(abbrev);
    return color.replace('0.8)', '1)');
}

/**
 * Create team scores bar chart.
 * Displays total Scrabble scores for each NHL team.
 *
 * @param {Array} teams - Array of team objects with {abbreviation, total_score, name}
 * @param {string} canvasId - ID of canvas element (default: 'teamScoresChart')
 * @returns {Chart} Chart.js instance
 */
function createTeamScoresChart(teams, canvasId = 'teamScoresChart') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element #${canvasId} not found`);
        return null;
    }

    const ctx = canvas.getContext('2d');

    // Sort teams by score (descending) for visual clarity
    const sortedTeams = [...teams].sort((a, b) => b.total_score - a.total_score);

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedTeams.map(t => t.abbreviation || t.abbrev),
            datasets: [{
                label: 'Team Total Score',
                data: sortedTeams.map(t => t.total_score),
                backgroundColor: sortedTeams.map(t => getTeamColor(t.abbreviation || t.abbrev)),
                borderColor: sortedTeams.map(t => getTeamBorderColor(t.abbreviation || t.abbrev)),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'NHL Teams by Scrabble Score',
                    font: {
                        size: 18,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const team = sortedTeams[context.dataIndex];
                            return [
                                `Score: ${context.parsed.y}`,
                                `Team: ${team.name || team.abbreviation}`
                            ];
                        }
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Total Scrabble Score'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Team'
                    }
                }
            }
        }
    });
}

/**
 * Create score buckets for histogram.
 * Groups players into score ranges (0-10, 11-20, 21-30, etc.).
 *
 * @param {Array} players - Array of player objects with {score}
 * @param {number} bucketSize - Size of each bucket (default: 10)
 * @returns {Object} {labels: string[], counts: number[]}
 */
function createScoreBuckets(players, bucketSize = 10) {
    if (!players || players.length === 0) {
        return { labels: [], counts: [] };
    }

    const maxScore = Math.max(...players.map(p => p.score || 0));
    const numBuckets = Math.ceil(maxScore / bucketSize);

    const buckets = Array(numBuckets).fill(0);

    players.forEach(p => {
        const score = p.score || 0;
        const bucketIndex = Math.floor(score / bucketSize);
        if (bucketIndex < numBuckets) {
            buckets[bucketIndex]++;
        }
    });

    return {
        labels: buckets.map((_, i) => `${i * bucketSize}-${(i + 1) * bucketSize - 1}`),
        counts: buckets
    };
}

/**
 * Create player score distribution histogram.
 * Shows how many players fall into each score range.
 *
 * @param {Array} players - Array of player objects with {score}
 * @param {string} canvasId - ID of canvas element (default: 'playerDistributionChart')
 * @returns {Chart} Chart.js instance
 */
function createPlayerDistributionChart(players, canvasId = 'playerDistributionChart') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element #${canvasId} not found`);
        return null;
    }

    const ctx = canvas.getContext('2d');
    const buckets = createScoreBuckets(players);

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: buckets.labels,
            datasets: [{
                label: 'Number of Players',
                data: buckets.counts,
                backgroundColor: 'rgba(75, 192, 192, 0.8)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Player Score Distribution',
                    font: {
                        size: 18,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Players: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Players'
                    },
                    ticks: {
                        stepSize: 10,
                        precision: 0
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Score Range'
                    }
                }
            }
        }
    });
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createTeamScoresChart,
        createPlayerDistributionChart,
        getTeamColor,
        getTeamBorderColor,
        createScoreBuckets
    };
}
