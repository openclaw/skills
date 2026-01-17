#!/usr/bin/env node

/**
 * Apple Docs CLI - Query Apple Developer Documentation and WWDC Videos
 *
 * Direct integration with Apple's developer documentation APIs.
 * No MCP server required.
 */

// ============ APPLE API CONSTANTS ============

const APPLE_URLS = {
  BASE: 'https://developer.apple.com',
  SEARCH: 'https://developer.apple.com/search/',
  DOCUMENTATION: 'https://developer.apple.com/documentation/',
  TUTORIALS_DATA: 'https://developer.apple.com/tutorials/data/',
  TECHNOLOGIES_JSON: 'https://developer.apple.com/tutorials/data/documentation/technologies.json',
  UPDATES_JSON: 'https://developer.apple.com/tutorials/data/documentation/Updates.json',
  UPDATES_INDEX_JSON: 'https://developer.apple.com/tutorials/data/index/updates',
  TECHNOLOGY_OVERVIEWS_JSON: 'https://developer.apple.com/tutorials/data/documentation/TechnologyOverviews.json',
  TECHNOLOGY_OVERVIEWS_INDEX_JSON: 'https://developer.apple.com/tutorials/data/index/technologyoverviews',
  SAMPLE_CODE_JSON: 'https://developer.apple.com/tutorials/data/documentation/SampleCode.json',
  SAMPLE_CODE_INDEX_JSON: 'https://developer.apple.com/tutorials/data/index/samplecode',
};

// WWDC data files bundled with the CLI
const WWDC_DATA = {
  INDEX: 'https://raw.githubusercontent.com/kimsungwhee/apple-docs-mcp/main/data/wwdc/index.json',
  VIDEOS: 'https://raw.githubusercontent.com/kimsungwhee/apple-docs-mcp/main/data/wwdc/all-videos.json',
  TOPICS: 'https://raw.githubusercontent.com/kimsungwhee/apple-docs-mcp/main/data/wwdc/topics.json',
  BY_TOPIC: (topic) => `https://raw.githubusercontent.com/kimsungwhee/apple-docs-mcp/main/data/wwdc/by-topic/${topic}.json`,
  BY_YEAR: (year) => `https://raw.githubusercontent.com/kimsungwhee/apple-docs-mcp/main/data/wwdc/by-year/${year}.json`,
  VIDEO_DATA: (year, id) => `https://raw.githubusercontent.com/kimsungwhee/apple-docs-mcp/main/data/wwdc/videos/${year}-${id}.json`,
};

// ============ HTTP CLIENT ============

async function httpFetch(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
      'Accept': 'text/html,application/json,application/xhtml+xml',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response;
}

async function fetchJson(url) {
  const response = await httpFetch(url);
  return response.json();
}

async function fetchText(url) {
  const response = await httpFetch(url);
  return response.text();
}

// ============ SEARCH ============

async function searchAppleDocs(query, limit = 10) {
  const url = `${APPLE_URLS.SEARCH}?q=${encodeURIComponent(query)}`;
  const html = await fetchText(url);
  return parseSearchResults(html, limit);
}

function parseSearchResults(html, limit) {
  const results = [];
  const regex = /<a[^>]+href="(\/documentation\/[^"]+)"[^>]*>([^<]+)<\/a>/gi;
  const seen = new Set();

  let match;
  let count = 0;
  while ((match = regex.exec(html)) !== null && count < limit) {
    const url = match[1];
    const title = match[2].trim().replace(/<[^>]*>/g, '');

    if (seen.has(url)) continue;
    seen.add(url);

    // Extract framework from URL
    const frameworkMatch = url.match(/\/documentation\/([^/]+)\//);
    const framework = frameworkMatch ? frameworkMatch[1] : null;

    // Skip non-docs URLs
    if (url.includes('/design/human-interface-guidelines/')) continue;
    if (url.includes('/download/')) continue;

    results.push({
      title: title || url.split('/').pop(),
      url: `https://developer.apple.com${url}`,
      framework,
      type: 'documentation'
    });
    count++;
  }

  return results;
}

// ============ SYMBOL SEARCH ============

async function searchFrameworkSymbols(query, limit = 20) {
  // Apple doesn't have a public symbol API, so we search docs
  const results = await searchAppleDocs(query, limit);
  return results;
}

// ============ FETCH DOC CONTENT ============

async function getAppleDocContent(url) {
  // Convert documentation URL to JSON API URL
  let jsonUrl = url;
  if (!url.includes('.json')) {
    jsonUrl = `https://developer.apple.com/tutorials/data${url}.json`;
  }

  try {
    const data = await fetchJson(jsonUrl);
    return formatDocContent(data);
  } catch {
    // Fallback to HTML
    const html = await fetchText(url);
    return extractDocFromHtml(html, url);
  }
}

function formatDocContent(data) {
  let output = [];
  output.push(`# ${data.title || 'Documentation'}`);
  if (data.framework) output.push(`\nFramework: ${data.framework}`);
  if (data.platforms) output.push(`\nPlatforms: ${data.platforms.join(', ')}`);
  output.push('\n');

  if (data.description) output.push(`${data.description}\n`);
  if (data.content) output.push(`\n${extractTextFromContent(data.content)}`);

  if (data.topics?.length) {
    output.push('\n\nTopics:\n');
    data.topics.forEach(t => output.push(`  - ${t}`));
  }

  if (data.relationships?.length) {
    output.push('\n\nRelationships:\n');
    data.relationships.forEach(r => {
      output.push(`  - ${r.type}: ${r.name || r.url}`);
    });
  }

  return output.join('\n');
}

function extractDocFromHtml(html, url) {
  // Simple extraction - get title and first paragraph
  const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
  const title = titleMatch ? titleMatch[1] : 'Apple Documentation';

  const descMatch = html.match(/<meta[^>]+name="description"[^>]+content="([^"]+)"/i) ||
                   html.match(/<p[^>]+class="description"[^>]*>([^<]+)/i);
  const description = descMatch ? descMatch[1] : '';

  return `# ${title}\n\nURL: ${url}\n\n${description}`;
}

function extractTextFromContent(content) {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) return content.map(c => extractTextFromContent(c)).join('\n');
  if (content.text) return content.text;
  return JSON.stringify(content);
}

// ============ LIST TECHNOLOGIES ============

async function listTechnologies() {
  const data = await fetchJson(APPLE_URLS.TECHNOLOGIES_JSON);
  return data;
}

// ============ RELATED APIS ============

async function getRelatedApis(symbolName) {
  // Search for the symbol in docs
  const results = await searchAppleDocs(symbolName, 5);
  return results;
}

// ============ PLATFORM COMPATIBILITY ============

async function getPlatformCompatibility(symbolName) {
  const results = await searchAppleDocs(`${symbolName} platform compatibility`, 5);
  return results;
}

// ============ SIMILAR APIS ============

async function findSimilarApis(symbolName) {
  const results = await searchAppleDocs(`${symbolName} alternative replacement`, 5);
  return results;
}

// ============ DOCUMENTATION UPDATES ============

async function getDocumentationUpdates(limit = 10) {
  try {
    const data = await fetchJson(APPLE_URLS.UPDATES_JSON);
    return (data.updates || data.slice(0, limit));
  } catch {
    return [{ error: 'Could not fetch updates' }];
  }
}

// ============ TECHNOLOGY OVERVIEWS ============

async function getTechnologyOverviews(technology) {
  try {
    const data = await fetchJson(APPLE_URLS.TECHNOLOGY_OVERVIEWS_JSON);
    const filtered = data.filter(t =>
      t.name?.toLowerCase().includes(technology.toLowerCase()) ||
      t.title?.toLowerCase().includes(technology.toLowerCase())
    );
    return filtered;
  } catch {
    return [{ error: 'Could not fetch technology overviews' }];
  }
}

// ============ SAMPLE CODE ============

async function getSampleCode(technology, limit = 10) {
  try {
    const data = await fetchJson(APPLE_URLS.SAMPLE_CODE_JSON);
    const filtered = (data.sampleCode || data)
      .filter(s => s.title?.toLowerCase().includes(technology.toLowerCase()))
      .slice(0, limit);
    return filtered;
  } catch {
    return [{ error: 'Could not fetch sample code' }];
  }
}

// ============ WWDC DATA ============

async function getWwdcIndex() {
  return fetchJson(WWDC_DATA.INDEX);
}

async function getWwdcVideos() {
  return fetchJson(WWDC_DATA.VIDEOS);
}

async function getWwdcTopics() {
  return fetchJson(WWDC_DATA.TOPICS);
}

async function searchWwdcVideos(query, year = null, limit = 10) {
  const data = await getWwdcVideos();
  let videos = data.videos || [];

  if (year) {
    videos = videos.filter(v => v.year === year);
  }

  if (query) {
    const q = query.toLowerCase();
    videos = videos.filter(v =>
      v.title?.toLowerCase().includes(q) ||
      v.topics?.some(t => t.toLowerCase().includes(q))
    );
  }

  return videos.slice(0, limit).map(v => ({
    id: v.id,
    year: v.year,
    title: v.title,
    topics: v.topics,
    url: v.url,
    hasTranscript: v.hasTranscript,
    hasCode: v.hasCode
  }));
}

async function getWwdcVideoDetails(videoId, includeTranscript = true) {
  // Parse video ID (format: "2024-100" or just "100")
  const match = videoId.match(/(\d{4})[-_]?(\d+)/);
  if (!match) {
    // Try to find by ID only
    const allVideos = await getWwdcVideos();
    const video = allVideos.videos?.find(v => v.id === videoId);
    if (video) {
      return formatWwdcVideo(video, includeTranscript);
    }
    return { error: 'Invalid video ID format. Use format: YYYY-NNN (e.g., 2024-100)' };
  }

  const year = match[1];
  const id = match[2];
  const videoDataUrl = WWDC_DATA.VIDEO_DATA(year, id);

  try {
    const videoData = await fetchJson(videoDataUrl);
    return formatWwdcVideoFull(videoData, includeTranscript);
  } catch {
    // Fallback to index data
    const allVideos = await getWwdcVideos();
    const video = allVideos.videos?.find(v => v.id === id && v.year === year);
    if (video) {
      return formatWwdcVideo(video, includeTranscript);
    }
    return { error: 'Video not found' };
  }
}

function formatWwdcVideo(video, includeTranscript) {
  let output = [];
  output.push(`# ${video.title}`);
  output.push(`\nYear: ${video.year} | Session: ${video.id}`);
  output.push(`\nURL: ${video.url}`);
  output.push(`\nTopics: ${video.topics?.join(', ') || 'N/A'}`);
  output.push(`\nTranscript: ${video.hasTranscript ? 'Available' : 'Not available'}`);
  output.push(`\nCode Samples: ${video.hasCode ? 'Available' : 'Not available'}`);

  if (includeTranscript && video.hasTranscript) {
    output.push(`\n\nTranscript URL: ${video.url}#transcript`);
  }

  return output.join('\n');
}

function formatWwdcVideoFull(videoData, includeTranscript) {
  let output = [];
  output.push(`# ${videoData.title || 'WWDC Session'}`);
  output.push(`\nYear: ${videoData.year || 'N/A'} | Session: ${videoData.sessionID || videoData.id || 'N/A'}`);

  if (videoData.presenters?.length) {
    output.push(`\nPresenters: ${videoData.presenters.join(', ')}`);
  }

  output.push(`\nURL: ${videoData.url}`);
  output.push(`\nTopics: ${videoData.topics?.join(', ') || 'N/A'}`);

  if (videoData.description) {
    output.push(`\n\n## Description\n${videoData.description}`);
  }

  if (videoData.relatedSessions?.length) {
    output.push(`\n\n## Related Sessions`);
    videoData.relatedSessions.forEach(s => {
      output.push(`  - ${s.title} (${s.year}-${s.sessionID})`);
    });
  }

  if (includeTranscript && videoData.transcript) {
    output.push(`\n\n## Transcript\n${videoData.transcript.substring(0, 2000)}...`);
    output.push(`\n\n[Full transcript available at: ${videoData.url}#transcript]`);
  }

  return output.join('\n');
}

async function listWwdcTopics() {
  const data = await getWwdcTopics();
  return data;
}

async function listWwdcYears() {
  const index = await getWwdcIndex();
  return {
    years: index.years || [],
    totalVideos: index.totalVideos || 0
  };
}

// ============ OUTPUT FORMATTING ============

const colors = {
  reset: '\x1b[0m', bright: '\x1b[1m', dim: '\x1b[2m',
  green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m',
  red: '\x1b[31m', cyan: '\x1b[36m', magenta: '\x1b[35m', white: '\x1b[37m'
};

function log(text = '', color = 'reset') {
  console.log(`${colors[color]}${text}${colors.reset}`);
}

function logError(text) {
  console.error(`${colors.red}Error: ${text}${colors.reset}`);
}

function outputJson(data) {
  console.log(JSON.stringify(data, null, 2));
}

function outputResults(results, title) {
  if (!results || results.length === 0) {
    log('\nNo results found.', 'yellow');
    return;
  }

  log(`\n${title}`, 'bright');
  log('=' .repeat(50), 'dim');

  results.forEach((r, i) => {
    if (r.title) {
      log(`\n${i + 1}. ${r.title}`, 'cyan');
      if (r.framework) log(`   Framework: ${r.framework}`, 'dim');
      if (r.year) log(`   Year: ${r.year}`, 'dim');
      if (r.topics) log(`   Topics: ${r.topics.join(', ')}`, 'dim');
      log(`   URL: ${r.url}`, 'dim');
    } else {
      log(`\n${JSON.stringify(r)}`);
    }
  });
}

// ============ COMMANDS ============

async function cmdSearch(query, options = {}) {
  if (!query) {
    logError('Search query required');
    log('Usage: apple-docs search "SwiftUI animation"');
    process.exit(1);
  }

  log(`\nSearching Apple docs for: "${query}"`, 'bright');
  const results = await searchAppleDocs(query, options.limit || 10);
  outputResults(results, 'Search Results');
}

async function cmdSymbols(query, options = {}) {
  if (!query) {
    logError('Symbol query required');
    log('Usage: apple-docs symbols "UITableView"');
    process.exit(1);
  }

  log(`\nSearching for symbols: "${query}"`, 'bright');
  const results = await searchFrameworkSymbols(query, options.limit || 20);
  outputResults(results, 'Symbol Results');
}

async function cmdDoc(path) {
  if (!path) {
    logError('Documentation path required');
    log('Usage: apple-docs doc "/documentation/swiftui/view"');
    process.exit(1);
  }

  // Ensure URL is complete
  const url = path.startsWith('http') ? path : `https://developer.apple.com${path}`;

  log(`\nFetching documentation: ${url}`, 'bright');
  const content = await getAppleDocContent(url);
  log(`\n${content}`);
}

async function cmdTech() {
  log('\nListing Apple technologies...', 'bright');
  const data = await listTechnologies();
  outputJson(data);
}

async function cmdApis(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs apis "UIViewController"');
    process.exit(1);
  }

  log(`\nFinding related APIs for: "${symbol}"`, 'bright');
  const results = await getRelatedApis(symbol);
  outputResults(results, 'Related APIs');
}

async function cmdPlatform(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs platform "UIScrollView"');
    process.exit(1);
  }

  log(`\nChecking platform compatibility for: "${symbol}"`, 'bright');
  const results = await getPlatformCompatibility(symbol);
  outputResults(results, 'Platform Compatibility');
}

async function cmdSimilar(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs similar "UIPickerView"');
    process.exit(1);
  }

  log(`\nFinding similar/alternative APIs for: "${symbol}"`, 'bright');
  const results = await findSimilarApis(symbol);
  outputResults(results, 'Similar APIs');
}

async function cmdUpdates(options = {}) {
  log('\nFetching documentation updates...', 'bright');
  const updates = await getDocumentationUpdates(options.limit || 10);
  outputJson(updates);
}

async function cmdOverview(technology) {
  if (!technology) {
    logError('Technology name required');
    log('Usage: apple-docs overview "SwiftUI"');
    process.exit(1);
  }

  log(`\nFetching technology overview: ${technology}`, 'bright');
  const overviews = await getTechnologyOverviews(technology);
  outputJson(overviews);
}

async function cmdSamples(technology, options = {}) {
  if (!technology) {
    logError('Technology name required');
    log('Usage: apple-docs samples "SwiftUI"');
    process.exit(1);
  }

  log(`\nSearching sample code for: ${technology}`, 'bright');
  const samples = await getSampleCode(technology, options.limit || 10);
  outputJson(samples);
}

async function cmdWwdcSearch(query, options = {}) {
  if (!query) {
    logError('WWDC search query required');
    log('Usage: apple-docs wwdc-search "async await"');
    process.exit(1);
  }

  log(`\nSearching WWDC videos for: "${query}"`, 'bright');
  const results = await searchWwdcVideos(query, options.year, options.limit || 10);
  outputResults(results, 'WWDC Videos');
}

async function cmdWwdcVideo(id, options = {}) {
  if (!id) {
    logError('WWDC video ID required');
    log('Usage: apple-docs wwdc-video 2024-100');
    process.exit(1);
  }

  log(`\nFetching WWDC video details: ${id}`, 'bright');
  const details = await getWwdcVideoDetails(id, options.transcript !== false);
  if (typeof details === 'string') {
    log(`\n${details}`);
  } else {
    outputJson(details);
  }
}

async function cmdWwdcTopics() {
  log('\nListing WWDC topics...', 'bright');
  const topics = await listWwdcTopics();
  outputJson(topics);
}

async function cmdWwdcYears() {
  log('\nListing WWDC years...', 'bright');
  const data = await listWwdcYears();

  log(`\nWWDC Years (${data.totalVideos} total videos):`, 'bright');
  log('='.repeat(40), 'dim');

  data.years.forEach(year => {
    log(`\n  ${year}`, 'cyan');
  });
}

// ============ HELP ============

function showHelp() {
  log(`
${colors.bright}Apple Docs CLI${colors.reset} - Query Apple Developer Documentation and WWDC Videos
${colors.dim}Direct integration with Apple's developer APIs${colors.reset}

${colors.bright}SETUP:${colors.reset}
  No setup required - works out of the box.

${colors.bright}SEARCH COMMANDS:${colors.reset}
  apple-docs search "query"              Search Apple Developer Documentation
  apple-docs symbols "UIView"            Search framework classes, structs, protocols
  apple-docs doc "/path/to/doc"          Get detailed documentation by path

${colors.bright}API EXPLORATION:${colors.reset}
  apple-docs apis "UIViewController"     Find related APIs
  apple-docs platform "UIScrollView"     Check platform compatibility
  apple-docs similar "UIPickerView"      Find similar/recommended alternatives

${colors.bright}TECHNOLOGY BROWSING:${colors.reset}
  apple-docs tech                        List all Apple technologies
  apple-docs overview "SwiftUI"          Get technology overview guide
  apple-docs samples "SwiftUI"           Find sample code projects
  apple-docs updates                     Latest documentation updates

${colors.bright}WWDC VIDEOS:${colors.reset}
  apple-docs wwdc-search "async"         Search WWDC sessions (2014-2025)
  apple-docs wwdc-video 2024-100         Get video details and transcript
  apple-docs wwdc-topics                 List WWDC topic categories
  apple-docs wwdc-years                  List available WWDC years

${colors.bright}OPTIONS:${colors.reset}
  --limit <n>     Limit results (default varies)
  --category      Filter by technology category
  --framework     Filter by framework name
  --year          Filter by WWDC year
  --no-transcript Skip transcript for WWDC videos

${colors.bright}EXAMPLES:${colors.reset}
  ${colors.dim}# Search for SwiftUI animations${colors.reset}
  apple-docs search "SwiftUI animation"

  ${colors.dim}# Find UITableView delegate methods${colors.reset}
  apple-docs symbols "UITableViewDelegate"

  ${colors.dim}# Check iOS version support for Vision framework${colors.reset}
  apple-docs platform "VNRecognizeTextRequest"

  ${colors.dim}# Find WWDC sessions about async/await${colors.reset}
  apple-docs wwdc-search "async await"

  ${colors.dim}# Get a specific WWDC video${colors.reset}
  apple-docs wwdc-video 2024-100

  ${colors.dim}# List all available WWDC years${colors.reset}
  apple-docs wwdc-years
  `);
}

// ============ MAIN ============

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === 'help' || command === '-h') {
    showHelp();
    return;
  }

  // Parse options
  const options = {};
  let query = null;
  let i = 1;

  while (i < args.length) {
    const arg = args[i];

    if (arg.startsWith('--')) {
      const key = arg.substring(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());

      const valueOptions = ['limit', 'category', 'framework', 'year'];
      if (valueOptions.includes(key)) {
        options[key] = args[i + 1];
        i += 2;
      } else if (key === 'noTranscript') {
        options.transcript = false;
        i++;
      } else {
        options[key] = true;
        i++;
      }
    } else if (!arg.startsWith('-') && !['search', 'symbols', 'wwdc-search'].includes(command)) {
      if (command === 'doc') {
        options.path = arg;
      } else if (command === 'apis' || command === 'platform' || command === 'similar') {
        options.symbol = arg;
      } else if (command === 'tech' || command === 'overview') {
        options.technology = arg;
      } else if (command === 'samples') {
        options.technology = arg;
      } else if (command === 'wwdc-video') {
        options.id = arg;
      }
      i++;
    } else {
      i++;
    }
  }

  // Handle positional query for search commands
  if (command === 'search' || command === 'symbols' || command === 'wwdc-search') {
    query = args.slice(1).find(a => !a.startsWith('-')) || '';
  }

  // Route commands
  try {
    switch (command) {
      case 'search':
        await cmdSearch(query, options);
        break;
      case 'doc':
        await cmdDoc(options.path, options);
        break;
      case 'tech':
        await cmdTech(options);
        break;
      case 'symbols':
        await cmdSymbols(query, options);
        break;
      case 'apis':
        await cmdApis(options.symbol, options);
        break;
      case 'platform':
        await cmdPlatform(options.symbol, options);
        break;
      case 'similar':
        await cmdSimilar(options.symbol, options);
        break;
      case 'updates':
        await cmdUpdates(options);
        break;
      case 'overview':
        await cmdOverview(options.technology, options);
        break;
      case 'samples':
        await cmdSamples(options.technology, options);
        break;
      case 'wwdc-search':
        await cmdWwdcSearch(query, options);
        break;
      case 'wwdc-video':
        await cmdWwdcVideo(options.id, options);
        break;
      case 'wwdc-topics':
        await cmdWwdcTopics();
        break;
      case 'wwdc-years':
        await cmdWwdcYears();
        break;
      default:
        logError(`Unknown command: ${command}`);
        log('Run: apple-docs --help');
        process.exit(1);
    }
  } catch (err) {
    logError(err.message);
    process.exit(1);
  }
}

main().catch(err => {
  logError(err.message);
  process.exit(1);
});
