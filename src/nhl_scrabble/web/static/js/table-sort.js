/**
 * NHL Scrabble Analyzer - Table Sorting
 * Client-side table sorting for teams and players tables
 */

/**
 * TableSort - Makes HTML tables sortable by clicking column headers.
 *
 * Usage:
 *   new TableSort('myTableId');
 *
 * HTML Requirements:
 *   - Table must have id attribute
 *   - Headers with data-sort attribute will be sortable
 *   - Use data-sort-type="number" for numeric columns
 *   - Use data-sort-type="string" for text columns (default)
 *
 * Example:
 *   <table id="teamsTable">
 *     <thead>
 *       <tr>
 *         <th data-sort="rank" data-sort-type="number">Rank</th>
 *         <th data-sort="team" data-sort-type="string">Team</th>
 *         <th data-sort="score" data-sort-type="number">Score</th>
 *       </tr>
 *     </thead>
 *     <tbody><!-- rows --></tbody>
 *   </table>
 */
class TableSort {
    /**
     * Create a sortable table.
     *
     * @param {string} tableId - ID of the table element
     */
    constructor(tableId) {
        this.table = document.getElementById(tableId);
        if (!this.table) {
            console.warn(`Table #${tableId} not found`);
            return;
        }

        this.tbody = this.table.querySelector('tbody');
        this.headers = this.table.querySelectorAll('th[data-sort]');
        this.currentSort = {
            column: null,
            direction: 'asc'
        };

        if (this.headers.length === 0) {
            console.warn(`No sortable headers found in table #${tableId}`);
            return;
        }

        this.init();
    }

    /**
     * Initialize sorting functionality.
     * Adds click handlers and sort indicators to headers.
     */
    init() {
        this.headers.forEach(header => {
            // Make header clickable
            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';
            header.setAttribute('role', 'button');
            header.setAttribute('tabindex', '0');

            // Add click handler
            header.addEventListener('click', () => this.handleHeaderClick(header));

            // Add keyboard handler (Enter/Space)
            header.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleHeaderClick(header);
                }
            });

            // Add sort indicator icon
            const indicator = document.createElement('span');
            indicator.className = 'sort-indicator';
            indicator.innerHTML = ' ↕️';
            indicator.setAttribute('aria-hidden', 'true');
            header.appendChild(indicator);
        });
    }

    /**
     * Handle header click event.
     * Sorts table by clicked column.
     *
     * @param {HTMLElement} header - The clicked header element
     */
    handleHeaderClick(header) {
        const column = header.dataset.sort;
        const type = header.dataset.sortType || 'string';

        // Toggle direction if same column, otherwise reset to ascending
        if (this.currentSort.column === column) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.column = column;
            this.currentSort.direction = 'asc';
        }

        this.sortTable(column, type, this.currentSort.direction);
        this.updateSortIndicators();

        // Announce sort to screen readers
        this.announceSort(header, this.currentSort.direction);
    }

    /**
     * Sort the table by specified column.
     *
     * @param {string} column - Column identifier (data-sort value)
     * @param {string} type - Sort type ('number' or 'string')
     * @param {string} direction - Sort direction ('asc' or 'desc')
     */
    sortTable(column, type, direction) {
        const columnIndex = this.getColumnIndex(column);
        if (columnIndex === -1) {
            console.warn(`Column ${column} not found`);
            return;
        }

        const rows = Array.from(this.tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            const aCell = a.cells[columnIndex];
            const bCell = b.cells[columnIndex];

            if (!aCell || !bCell) {
                return 0;
            }

            // Get text content or data-value attribute
            const aValue = aCell.dataset.value || aCell.textContent.trim();
            const bValue = bCell.dataset.value || bCell.textContent.trim();

            let comparison = 0;

            if (type === 'number') {
                // Parse as numbers, handle non-numeric values
                const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
                const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
                comparison = (isNaN(aNum) ? 0 : aNum) - (isNaN(bNum) ? 0 : bNum);
            } else {
                // String comparison (case-insensitive)
                comparison = aValue.toLowerCase().localeCompare(bValue.toLowerCase());
            }

            return direction === 'asc' ? comparison : -comparison;
        });

        // Re-append rows in sorted order
        rows.forEach(row => this.tbody.appendChild(row));
    }

    /**
     * Get column index by data-sort attribute.
     *
     * @param {string} column - Column identifier
     * @returns {number} Column index or -1 if not found
     */
    getColumnIndex(column) {
        const headersArray = Array.from(this.headers);
        const headerIndex = headersArray.findIndex(h => h.dataset.sort === column);

        if (headerIndex === -1) {
            return -1;
        }

        // Get the actual column index in the table
        const allHeaders = Array.from(this.table.querySelectorAll('th'));
        return allHeaders.indexOf(headersArray[headerIndex]);
    }

    /**
     * Update sort indicators on all headers.
     * Shows arrow for sorted column, neutral indicator for others.
     */
    updateSortIndicators() {
        this.headers.forEach(header => {
            const indicator = header.querySelector('.sort-indicator');
            if (!indicator) return;

            if (header.dataset.sort === this.currentSort.column) {
                // Active column: show direction arrow
                indicator.innerHTML = this.currentSort.direction === 'asc' ? ' ↑' : ' ↓';
                indicator.style.opacity = '1';
                header.setAttribute('aria-sort', this.currentSort.direction === 'asc' ? 'ascending' : 'descending');
            } else {
                // Inactive columns: show neutral indicator
                indicator.innerHTML = ' ↕️';
                indicator.style.opacity = '0.3';
                header.removeAttribute('aria-sort');
            }
        });
    }

    /**
     * Announce sort to screen readers.
     *
     * @param {HTMLElement} header - Sorted header element
     * @param {string} direction - Sort direction
     */
    announceSort(header, direction) {
        const columnName = header.textContent.replace(/[↑↓↕️]/g, '').trim();
        const announcement = `Sorted by ${columnName}, ${direction === 'asc' ? 'ascending' : 'descending'}`;

        // Create or update live region for screen readers
        let liveRegion = document.getElementById('sort-announcement');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'sort-announcement';
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }

        liveRegion.textContent = announcement;
    }

    /**
     * Reset table to original order.
     * Optionally provide a comparator function for custom default order.
     *
     * @param {Function} [comparator] - Optional comparator function
     */
    reset(comparator = null) {
        const rows = Array.from(this.tbody.querySelectorAll('tr'));

        if (comparator) {
            rows.sort(comparator);
        } else {
            // Reset to DOM order (assumes original order is preserved in data-original-index)
            rows.sort((a, b) => {
                const aIndex = parseInt(a.dataset.originalIndex || a.rowIndex);
                const bIndex = parseInt(b.dataset.originalIndex || b.rowIndex);
                return aIndex - bIndex;
            });
        }

        rows.forEach(row => this.tbody.appendChild(row));
        this.currentSort = { column: null, direction: 'asc' };
        this.updateSortIndicators();
    }
}

/**
 * Initialize all sortable tables on the page.
 * Looks for tables with class 'sortable' or data-sortable attribute.
 */
function initializeSortableTables() {
    const sortableTables = document.querySelectorAll('table.sortable, table[data-sortable]');
    sortableTables.forEach(table => {
        if (table.id) {
            new TableSort(table.id);
        } else {
            console.warn('Sortable table found without id attribute:', table);
        }
    });
}

// Auto-initialize on DOMContentLoaded
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeSortableTables);
    } else {
        // DOM already loaded
        initializeSortableTables();
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TableSort, initializeSortableTables };
}
