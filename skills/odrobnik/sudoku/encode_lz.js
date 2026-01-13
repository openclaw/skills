const LZString = require('./lz-string.js');

// Get JSON from args
const jsonStr = process.argv[2];
if (!jsonStr) {
    console.error("Usage: node encode_lz.js <json_string>");
    process.exit(1);
}

// Compress to a URL-safe payload for SudokuPad /puzzle/ links.
// Use compressToBase64 to align with SudokuPad's expected decoding.
// This produces '+', '/', '='.
const compressed = LZString.compressToBase64(jsonStr);
console.log(compressed);
