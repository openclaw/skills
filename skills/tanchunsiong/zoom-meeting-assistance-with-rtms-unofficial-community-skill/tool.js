// Utility functions for the RTMS meeting assistant

/**
 * Sanitize filename to avoid invalid characters
 * Replaces problematic characters with underscores
 * @param {string} name - The filename or path to sanitize
 * @returns {string} - The sanitized filename
 */
export function sanitizeFileName(name) {
  return name.replace(/[<>:"\/\\|?*=\s]/g, '_');
}
