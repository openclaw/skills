/**
 * Calculate Levenshtein distance between two strings
 * @param {string} a First string
 * @param {string} b Second string
 * @returns {number} Edit distance
 */
function levenshteinDistance(a, b) {
  const matrix = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1,     // insertion
          matrix[i - 1][j] + 1      // deletion
        );
      }
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Find best match for a query string in a list of items
 * @param {string} query Search query
 * @param {Array} items Array of items with 'name' property
 * @param {number} threshold Maximum distance threshold (default: 5)
 * @returns {object|null} Best matching item or null
 */
function fuzzyMatch(query, items, threshold = 5) {
  const queryLower = query.toLowerCase();
  
  // First try exact match
  const exactMatch = items.find(item => 
    item.name.toLowerCase() === queryLower
  );
  if (exactMatch) return exactMatch;

  // Then try substring match
  const substringMatch = items.find(item => 
    item.name.toLowerCase().includes(queryLower) || 
    queryLower.includes(item.name.toLowerCase())
  );
  if (substringMatch) return substringMatch;

  // Finally try Levenshtein distance
  let bestMatch = null;
  let bestDistance = Infinity;

  for (const item of items) {
    const distance = levenshteinDistance(queryLower, item.name.toLowerCase());
    if (distance < bestDistance && distance <= threshold) {
      bestDistance = distance;
      bestMatch = item;
    }
  }

  return bestMatch;
}

/**
 * Find all matches above a similarity threshold
 * @param {string} query Search query
 * @param {Array} items Array of items with 'name' property
 * @param {number} limit Maximum number of results
 * @returns {Array} Sorted array of matches
 */
function fuzzySearch(query, items, limit = 5) {
  const queryLower = query.toLowerCase();
  const results = [];

  for (const item of items) {
    const nameLower = item.name.toLowerCase();
    let score = 0;

    // Exact match
    if (nameLower === queryLower) {
      score = 1000;
    }
    // Starts with query
    else if (nameLower.startsWith(queryLower)) {
      score = 500;
    }
    // Contains query
    else if (nameLower.includes(queryLower)) {
      score = 250;
    }
    // Levenshtein distance
    else {
      const distance = levenshteinDistance(queryLower, nameLower);
      if (distance <= 5) {
        score = 100 - (distance * 10);
      }
    }

    if (score > 0) {
      results.push({ item, score });
    }
  }

  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(r => r.item);
}

module.exports = {
  levenshteinDistance,
  fuzzyMatch,
  fuzzySearch
};
