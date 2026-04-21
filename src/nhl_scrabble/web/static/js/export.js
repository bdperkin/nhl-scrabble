/**
 * NHL Scrabble Analyzer - Data Export
 * Client-side data export functionality (CSV, JSON)
 */

/**
 * DataExporter - Handles exporting table data to various formats.
 *
 * Supports:
 * - CSV export
 * - JSON export
 * - Client-side file download
 */
class DataExporter {
    /**
     * Export data to CSV format and trigger download.
     *
     * @param {Array<Object>} data - Array of objects to export
     * @param {string} filename - Output filename (without extension)
     */
    static exportToCSV(data, filename) {
        if (!data || data.length === 0) {
            console.warn('No data to export');
            return;
        }

        const csv = this.convertToCSV(data);
        this.downloadFile(csv, `${filename}.csv`, 'text/csv;charset=utf-8;');
    }

    /**
     * Export data to JSON format and trigger download.
     *
     * @param {Array<Object>|Object} data - Data to export
     * @param {string} filename - Output filename (without extension)
     */
    static exportToJSON(data, filename) {
        if (!data) {
            console.warn('No data to export');
            return;
        }

        const json = JSON.stringify(data, null, 2);
        this.downloadFile(json, `${filename}.json`, 'application/json;charset=utf-8;');
    }

    /**
     * Convert array of objects to CSV format.
     * Handles proper escaping and quoting.
     *
     * @param {Array<Object>} data - Array of objects
     * @returns {string} CSV string
     */
    static convertToCSV(data) {
        if (data.length === 0) return '';

        // Get headers from first object
        const headers = Object.keys(data[0]);
        const csvRows = [];

        // Add header row
        csvRows.push(headers.join(','));

        // Add data rows
        data.forEach(row => {
            const values = headers.map(header => {
                let value = row[header];

                // Handle null/undefined
                if (value === null || value === undefined) {
                    return '';
                }

                // Convert to string
                value = String(value);

                // Escape and quote if necessary
                if (value.includes(',') || value.includes('"') || value.includes('\n')) {
                    // Escape quotes by doubling them
                    value = value.replace(/"/g, '""');
                    // Wrap in quotes
                    value = `"${value}"`;
                }

                return value;
            });
            csvRows.push(values.join(','));
        });

        return csvRows.join('\n');
    }

    /**
     * Trigger file download in browser.
     *
     * @param {string} content - File content
     * @param {string} filename - Filename including extension
     * @param {string} mimeType - MIME type
     */
    static downloadFile(content, filename, mimeType) {
        // Create blob
        const blob = new Blob([content], { type: mimeType });

        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';

        // Trigger download
        document.body.appendChild(link);
        link.click();

        // Cleanup
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**
     * Extract data from HTML table.
     * Reads table rows and converts to array of objects.
     *
     * @param {string|HTMLElement} tableIdOrElement - Table ID or element
     * @returns {Array<Object>} Array of row objects
     */
    static extractTableData(tableIdOrElement) {
        const table = typeof tableIdOrElement === 'string'
            ? document.getElementById(tableIdOrElement)
            : tableIdOrElement;

        if (!table) {
            console.warn('Table not found');
            return [];
        }

        const headers = Array.from(table.querySelectorAll('thead th')).map(th => {
            // Use data-export-name if available, otherwise use text content
            return th.dataset.exportName || th.textContent.trim().replace(/[↑↓↕️]/g, '').trim();
        });

        const rows = Array.from(table.querySelectorAll('tbody tr'));

        return rows.map(row => {
            const cells = Array.from(row.cells);
            const rowData = {};

            cells.forEach((cell, index) => {
                if (index < headers.length) {
                    // Use data-value if available (for formatted numbers)
                    const value = cell.dataset.value || cell.textContent.trim();
                    rowData[headers[index]] = value;
                }
            });

            return rowData;
        });
    }
}

/**
 * Setup export buttons for a table.
 * Automatically wires up CSV and JSON export buttons.
 *
 * @param {string} tableId - Table element ID
 * @param {string} baseName - Base filename for exports (without extension)
 * @param {Object} options - Optional configuration
 * @param {string} [options.csvButtonId] - CSV button ID
 * @param {string} [options.jsonButtonId] - JSON button ID
 */
function setupTableExport(tableId, baseName, options = {}) {
    const table = document.getElementById(tableId);
    if (!table) {
        console.warn(`Table #${tableId} not found`);
        return;
    }

    // Get or create export container
    let exportContainer = table.parentElement.querySelector('.export-buttons');
    if (!exportContainer && options.createButtons) {
        exportContainer = document.createElement('div');
        exportContainer.className = 'export-buttons';
        table.parentElement.insertBefore(exportContainer, table);
    }

    // Setup CSV export
    const csvButtonId = options.csvButtonId || `export-${tableId}-csv`;
    let csvButton = document.getElementById(csvButtonId);

    if (!csvButton && exportContainer && options.createButtons) {
        csvButton = document.createElement('button');
        csvButton.id = csvButtonId;
        csvButton.className = 'btn btn-secondary btn-sm';
        csvButton.innerHTML = '<span class="icon">📊</span> Export CSV';
        exportContainer.appendChild(csvButton);
    }

    if (csvButton) {
        csvButton.addEventListener('click', function() {
            const data = DataExporter.extractTableData(tableId);
            DataExporter.exportToCSV(data, `${baseName}-${getTimestamp()}`);
        });
    }

    // Setup JSON export
    const jsonButtonId = options.jsonButtonId || `export-${tableId}-json`;
    let jsonButton = document.getElementById(jsonButtonId);

    if (!jsonButton && exportContainer && options.createButtons) {
        jsonButton = document.createElement('button');
        jsonButton.id = jsonButtonId;
        jsonButton.className = 'btn btn-secondary btn-sm';
        jsonButton.innerHTML = '<span class="icon">📄</span> Export JSON';
        exportContainer.appendChild(jsonButton);
    }

    if (jsonButton) {
        jsonButton.addEventListener('click', function() {
            const data = DataExporter.extractTableData(tableId);
            DataExporter.exportToJSON(data, `${baseName}-${getTimestamp()}`);
        });
    }
}

/**
 * Get current timestamp for filenames.
 * Format: YYYYMMDD-HHMMSS
 *
 * @returns {string} Formatted timestamp
 */
function getTimestamp() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    return `${year}${month}${day}-${hours}${minutes}${seconds}`;
}

/**
 * Initialize export functionality on page load.
 * Auto-detects tables with data-export attribute.
 */
function initializeExportButtons() {
    const exportableTables = document.querySelectorAll('table[data-export]');
    exportableTables.forEach(table => {
        const baseName = table.dataset.export || table.id || 'data';
        if (table.id) {
            setupTableExport(table.id, baseName);
        }
    });
}

// Auto-initialize on DOMContentLoaded
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeExportButtons);
    } else {
        initializeExportButtons();
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DataExporter,
        setupTableExport,
        initializeExportButtons,
        getTimestamp
    };
}
