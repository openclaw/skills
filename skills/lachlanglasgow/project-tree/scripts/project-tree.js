#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration
const ROOT_DIR = path.join(os.homedir(), 'projects'); // Projects folder location (~/projects)
const MAX_DEPTH = 3;
const EXCLUDE_DIRS = [
  'node_modules',
  '.git',
  'dist',
  'build',
  'coverage',
  '.next',
  '.nuxt',
  '.cache',
  '__pycache__',
  'venv',
  'env',
  '.venv',
  '.env'
];
const EXCLUDE_FILES = [
  '.DS_Store',
  'Thumbs.db',
  '*.log',
  '*.lock',
  '.gitignore',
  '.gitattributes',
  '*.pyc',
  '*.pyo',
  '*.pyd',
  // JSON files
  '*.json',
  // Image files
  '*.png',
  '*.jpg',
  '*.jpeg',
  '*.gif',
  '*.svg',
  '*.ico',
  '*.bmp',
  '*.webp',
  '*.tiff',
  '*.tif',
  // Zip files
  '*.zip',
  '*.tar',
  '*.gz',
  '*.rar',
  '*.7z'
];

function shouldExclude(itemPath, isDirectory) {
  const basename = path.basename(itemPath);
  
  // Always show directories
  if (isDirectory) {
    return EXCLUDE_DIRS.includes(basename);
  }
  
  // Only show .md files (and directories which are handled above)
  return !basename.endsWith('.md');
}

function findPatternGroups(items, dirPath) {
  const groups = [];
  const used = new Set();
  
  // Look for numeric patterns like script1, script2, etc.
  const numericPattern = /^(\D+)(\d+)(\D*)$/;
  
  for (let i = 0; i < items.length; i++) {
    if (used.has(i)) continue;
    
    const item = items[i];
    const itemPath = path.join(dirPath, item);
    const match = item.match(numericPattern);
    
    if (match) {
      const [, prefix, numStr, suffix] = match;
      const num = parseInt(numStr);
      
      // Look for consecutive sequence
      const sequence = [{index: i, name: item, num: num}];
      let nextNum = num + 1;
      
      for (let j = i + 1; j < items.length; j++) {
        if (used.has(j)) continue;
        
        const nextItem = items[j];
        const nextMatch = nextItem.match(numericPattern);
        
        if (nextMatch && nextMatch[1] === prefix && nextMatch[3] === suffix) {
          const nextItemNum = parseInt(nextMatch[2]);
          if (nextItemNum === nextNum) {
            sequence.push({index: j, name: nextItem, num: nextItemNum});
            nextNum++;
          } else {
            break;
          }
        } else {
          break;
        }
      }
      
      if (sequence.length >= 3) {
        // Found a sequence of 3 or more
        const startNum = sequence[0].num;
        const endNum = sequence[sequence.length - 1].num;
        const groupName = `${prefix}[${startNum}-${endNum}]${suffix}`;
        const isDirectory = fs.statSync(path.join(dirPath, sequence[0].name)).isDirectory();
        
        groups.push({
          type: 'group',
          name: groupName,
          count: sequence.length,
          isDirectory: isDirectory
        });
        
        sequence.forEach(item => used.add(item.index));
        continue;
      }
    }
    
    // No pattern match, add as individual item
    const isDirectory = fs.statSync(itemPath).isDirectory();
    groups.push({
      type: 'item',
      name: item,
      isDirectory: isDirectory
    });
  }
  
  return groups;
}

function generateTree(dir, prefix = '', depth = 0) {
  if (depth > MAX_DEPTH) return '';
  
  let tree = '';
  
  try {
    const items = fs.readdirSync(dir).sort((a, b) => {
      const aPath = path.join(dir, a);
      const bPath = path.join(dir, b);
      const aIsDir = fs.statSync(aPath).isDirectory();
      const bIsDir = fs.statSync(bPath).isDirectory();
      
      if (aIsDir && !bIsDir) return -1;
      if (!aIsDir && bIsDir) return 1;
      return a.localeCompare(b);
    });
    
    // Find pattern groups
    const groups = findPatternGroups(items, dir);
    
    for (let i = 0; i < groups.length; i++) {
      const group = groups[i];
      const isLast = i === groups.length - 1;
      const connector = isLast ? '└── ' : '├── ';
      
      if (group.type === 'group') {
        const extension = group.isDirectory ? '/' : '';
        tree += `${prefix}${connector}${group.name}${extension} (${group.count} items)\n`;
      } else {
        const itemPath = path.join(dir, group.name);
        const isDirectory = fs.statSync(itemPath).isDirectory();
        
        if (shouldExclude(itemPath, isDirectory)) continue;
        
        const extension = isDirectory ? '/' : '';
        tree += `${prefix}${connector}${group.name}${extension}\n`;
        
        if (isDirectory && depth < MAX_DEPTH) {
          const newPrefix = prefix + (isLast ? '    ' : '│   ');
          tree += generateTree(itemPath, newPrefix, depth + 1);
        }
      }
    }
  } catch (err) {
    // Skip directories we can't read
  }
  
  return tree;
}

function updateMemory() {
  const treeOutput = generateTree(ROOT_DIR);
  const timestamp = new Date().toISOString();
  const memoryContent = `<!-- PROJECT_TREE_START -->
# Current Project Tree (${timestamp})
Generated with max depth ${MAX_DEPTH}, excluding dependency folders and files.

\`\`\`
~/projects/
${treeOutput}
\`\`\`
<!-- PROJECT_TREE_END -->`;
  
  // Read current MEMORY.md file
  const memoryPath = '/home/kevin/clawd/MEMORY.md';
  let existingContent = '';
  
  if (fs.existsSync(memoryPath)) {
    existingContent = fs.readFileSync(memoryPath, 'utf8');
  }
  
  // Replace or add the tree section
  const treeRegex = /<!-- PROJECT_TREE_START -->[\s\S]*?<!-- PROJECT_TREE_END -->/;
  let newContent;
  
  if (treeRegex.test(existingContent)) {
    newContent = existingContent.replace(treeRegex, memoryContent);
  } else {
    // Append to the end if no existing tree section found
    newContent = existingContent.trim() + '\n\n' + memoryContent;
  }
  
  // Write back to MEMORY.md
  fs.writeFileSync(memoryPath, newContent.trim() + '\n');
  
  console.log('Project tree updated in MEMORY.md');
  console.log(treeOutput);
}

// Run if called directly
if (require.main === module) {
  updateMemory();
}

module.exports = { updateMemory };