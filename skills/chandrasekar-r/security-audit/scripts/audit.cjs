#!/usr/bin/env node
/**
 * security-audit.cjs - Comprehensive security scanner for Clawdbot
 * Usage: node audit.js [--full] [--json] [--credentials] [--ports] [--configs] [--permissions] [--docker]
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Configuration
const CLAWDBOT_DIR = '/root/clawd';
const CONFIG_DIR = '/root/clawd/skills/.env';
const DOCKER_DIR = '/root/clawd';

// Results collection
const findings = [];
let checkCount = 0;
let criticalCount = 0;
let highCount = 0;

// Helper functions
function log(level, category, message, details = null) {
  const emoji = {
    CRITICAL: '🔴',
    HIGH: '🟠',
    MEDIUM: '🟡',
    LOW: '🟢',
    INFO: '🔵'
  };
  
  findings.push({
    level,
    category,
    message,
    details,
    timestamp: new Date().toISOString()
  });
  
  checkCount++;
  if (level === 'CRITICAL') criticalCount++;
  if (level === 'HIGH') highCount++;
}

function checkFileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
}

function scanFileForPatterns(filePath, patterns, category) {
  if (!checkFileExists(filePath)) return;
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    for (const pattern of patterns) {
      if (pattern.regex.test(content)) {
        log(pattern.level, category, pattern.message, {
          file: filePath,
          match: pattern.match
        });
      }
    }
  } catch (e) {
    // Ignore unreadable files
  }
}

function getFilesRecursively(dir, extensions = ['.js', '.ts', '.json', '.env', '.md', '.yml', '.yaml']) {
  const files = [];
  
  function traverse(currentDir) {
    try {
      const entries = fs.readdirSync(currentDir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(currentDir, entry.name);
        
        if (entry.isDirectory()) {
          if (!entry.name.startsWith('.') && !entry.name.includes('node_modules')) {
            traverse(fullPath);
          }
        } else if (extensions.some(ext => entry.name.endsWith(ext))) {
          files.push(fullPath);
        }
      }
    } catch {
      // Ignore inaccessible directories
    }
  }
  
  traverse(dir);
  return files;
}

// === CHECKS ===

function checkCredentials() {
  log('INFO', 'CREDENTIALS', 'Starting credential scan...');
  
  const credentialPatterns = [
    {
      level: 'CRITICAL',
      message: 'Potential API key found in file',
      regex: /api[_-]?key\s*[:=]\s*['"'][a-zA-Z0-9]{20,}['"']/gi,
      match: 'API key pattern'
    },
    {
      level: 'CRITICAL',
      message: 'Potential secret token found',
      regex: /(secret|token|auth)[_-]?key\s*[:=]\s*['"'][a-zA-Z0-9_\-]{30,}['"']/gi,
      match: 'Secret pattern'
    },
    {
      level: 'HIGH',
      message: 'Hardcoded password found',
      regex: /password\s*[:=]\s*['"'][^'"']{8,}['"']/gi,
      match: 'Password pattern'
    },
    {
      level: 'HIGH',
      message: 'Private key detected',
      regex: /-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----/g,
      match: 'Private key'
    },
    {
      level: 'MEDIUM',
      message: 'URL with credentials found',
      regex: /https?:\/\/[^:]+:[^@]+@/g,
      match: 'URL with credentials'
    }
  ];
  
  // Scan key files
  const keyFiles = [
    CONFIG_DIR,
    path.join(CLAWDBOT_DIR, 'skills/.env'),
    path.join(CLAWDBOT_DIR, '.env'),
    path.join(CLAWDBOT_DIR, 'config.json')
  ];
  
  for (const file of keyFiles) {
    scanFileForPatterns(file, credentialPatterns, 'CREDENTIALS');
  }
  
  // Scan all code files
  const codeFiles = getFilesRecursively(CLAWDBOT_DIR);
  
  for (const file of codeFiles) {
    if (file.includes('node_modules') || file.includes('.git')) continue;
    scanFileForPatterns(file, credentialPatterns.filter(p => p.level !== 'CRITICAL'), 'CREDENTIALS');
  }
  
  log('INFO', 'CREDENTIALS', `Scanned ${codeFiles.length} files`);
}

function checkPorts() {
  log('INFO', 'PORTS', 'Checking for open ports...');
  
  try {
    // Check if ss or netstat is available
    const ssResult = execSync('ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || echo "not available"', 
      { encoding: 'utf8', timeout: 5000 });
    
    const ports = [];
    const lines = ssResult.split('\n');
    
    for (const line of lines) {
      const portMatch = line.match(/:(\d+)\s/);
      if (portMatch) {
        const port = parseInt(portMatch[1]);
        if (port > 1024 && !ports.includes(port)) {
          ports.push(port);
        }
      }
    }
    
    if (ports.length > 0) {
      log('MEDIUM', 'PORTS', `Found ${ports.length} open ports`, { ports });
    } else {
      log('INFO', 'PORTS', 'No unexpected open ports detected');
    }
  } catch {
    log('LOW', 'PORTS', 'Could not scan ports (tool not available)');
  }
}

function checkConfigs() {
  log('INFO', 'CONFIGS', 'Validating configuration security...');
  
  // Check for .env file
  if (!checkFileExists(CONFIG_DIR)) {
    log('HIGH', 'CONFIGS', 'No .env file found - credentials may not be configured');
    return;
  }
  
  try {
    const envContent = fs.readFileSync(CONFIG_DIR, 'utf8');
    
    // Check for rate limiting config
    if (!envContent.includes('RATE_LIMIT')) {
      log('MEDIUM', 'CONFIGS', 'No RATE_LIMIT configuration found');
    }
    
    // Check for auth settings
    if (!envContent.includes('AUTH_') && !envContent.includes('API_KEY')) {
      log('HIGH', 'CONFIGS', 'No authentication configuration detected');
    }
    
    // Check for log level
    if (envContent.includes('LOG_LEVEL=debug') || envContent.includes('LOG_LEVEL=DEBUG')) {
      log('MEDIUM', 'CONFIGS', 'Debug logging enabled - may expose sensitive data');
    }
    
    // Check for CORS
    if (envContent.includes('CORS_ORIGIN=*') || envContent.includes('CORS_ALLOW_ALL=true')) {
      log('HIGH', 'CONFIGS', 'CORS configured to allow all origins');
    }
    
  } catch (e) {
    log('LOW', 'CONFIGS', 'Could not read configuration file');
  }
}

function checkPermissions() {
  log('INFO', 'PERMISSIONS', 'Checking file permissions...');
  
  const sensitivePatterns = [
    { pattern: /\.env$/, level: 'CRITICAL', message: 'World-readable .env file' },
    { pattern: /\.json$/, level: 'HIGH', message: 'World-readable JSON config' },
    { pattern: /\.key$/, level: 'CRITICAL', message: 'World-readable key file' },
    { pattern: /\.pem$/, level: 'CRITICAL', message: 'World-readable PEM file' }
  ];
  
  const files = getFilesRecursively(CLAWDBOT_DIR);
  
  for (const file of files) {
    try {
      const stats = fs.statSync(file);
      const mode = stats.mode & 0o777;
      
      // Check if world-readable
      if ((mode & 0o004) !== 0) {
        for (const sp of sensitivePatterns) {
          if (sp.pattern.test(file)) {
            log(sp.level, 'PERMISSIONS', sp.message, { file, mode: mode.toString(8) });
          }
        }
      }
      
      // Check if executable by all
      if ((mode & 0o001) !== 0 && file.endsWith('.js')) {
        log('MEDIUM', 'PERMISSIONS', `Executable JS file: ${path.basename(file)}`);
      }
    } catch {
      // Ignore inaccessible files
    }
  }
}

function checkDocker() {
  log('INFO', 'DOCKER', 'Checking Docker security...');
  
  const dockerFile = path.join(CLAWDBOT_DIR, 'Dockerfile');
  
  if (!checkFileExists(dockerFile)) {
    log('INFO', 'DOCKER', 'No Dockerfile found - skipping Docker checks');
    return;
  }
  
  try {
    const dockerContent = fs.readFileSync(dockerFile, 'utf8');
    
    if (dockerContent.includes('USER root') || !dockerContent.includes('USER ')) {
      log('HIGH', 'DOCKER', 'Container may run as root user');
    }
    
    if (dockerContent.includes('--privileged')) {
      log('CRITICAL', 'DOCKER', 'Container has privileged mode enabled');
    }
    
    if (!dockerContent.includes('HEALTHCHECK')) {
      log('LOW', 'DOCKER', 'No HEALTHCHECK instruction found');
    }
    
    if (dockerContent.includes(':latest') && !dockerContent.includes('BUILDARG')) {
      log('MEDIUM', 'DOCKER', 'Using floating tag :latest - consider specific version');
    }
    
  } catch (e) {
    log('LOW', 'DOCKER', 'Could not analyze Dockerfile');
  }
}

function checkGit() {
  log('INFO', 'GIT', 'Checking for exposed Git information...');
  
  const gitDir = path.join(CLAWDBOT_DIR, '.git');
  
  if (checkFileExists(gitDir)) {
    log('MEDIUM', 'GIT', '.git directory exists - ensure it is not web-accessible');
  }
  
  const gitIgnore = path.join(CLAWDBOT_DIR, '.gitignore');
  if (!checkFileExists(gitIgnore)) {
    log('LOW', 'GIT', 'No .gitignore file found');
  }
}

function checkRecentCommits() {
  log('INFO', 'HISTORY', 'Checking for credential exposure in recent commits...');
  
  try {
    const logOutput = execSync('git log --oneline -20 2>/dev/null || echo "not a git repo"', 
      { encoding: 'utf8', timeout: 5000 });
    
    // Check for secrets in commit messages (paranoid check)
    if (/secret|token|password|key|auth/i.test(logOutput)) {
      log('LOW', 'HISTORY', 'Recent commits contain security-related keywords in messages');
    }
  } catch {
    log('INFO', 'HISTORY', 'Not a Git repository or Git not available');
  }
}

// === MAIN ===

async function runAudit(options = {}) {
  const { full = false, json = false, credentials = false, ports = false, 
           configs = false, permissions = false, docker = false } = options;
  
  const runAll = full || (!credentials && !ports && !configs && !permissions && !docker);
  
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║       CLAWDBOT SECURITY AUDIT v1.0                         ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
  
  const startTime = Date.now();
  
  if (runAll || credentials) checkCredentials();
  if (runAll || ports) checkPorts();
  if (runAll || configs) checkConfigs();
  if (runAll || permissions) checkPermissions();
  if (runAll || docker) checkDocker();
  checkGit();
  checkRecentCommits();
  
  const duration = Date.now() - startTime;
  
  // Summary
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║                    AUDIT SUMMARY                            ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
  
  console.log(`Checks performed: ${checkCount}`);
  console.log(`🔴 Critical: ${criticalCount}`);
  console.log(`🟠 High: ${highCount}`);
  console.log(`Total findings: ${findings.length}`);
  console.log(`Duration: ${duration}ms\n`);
  
  // Critical issues first
  const criticalFindings = findings.filter(f => f.level === 'CRITICAL');
  if (criticalFindings.length > 0) {
    console.log('🔴 CRITICAL ISSUES (Immediate action required):');
    for (const f of criticalFindings) {
      console.log(`  • ${f.message}`);
      if (f.details?.file) console.log(`    File: ${f.details.file}`);
    }
    console.log('');
  }
  
  if (json) {
    console.log('\n=== JSON REPORT ===');
    console.log(JSON.stringify({
      summary: {
        checks: checkCount,
        critical: criticalCount,
        high: highCount,
        total: findings.length,
        duration_ms: duration,
        timestamp: new Date().toISOString()
      },
      findings
    }, null, 2));
  }
  
  // Recommendation
  if (criticalCount > 0) {
    console.log('\n⚠️  CRITICAL ISSUES FOUND - Do not deploy until fixed!');
    process.exitCode = 1;
  } else if (highCount > 0) {
    console.log('\n⚠️  High-risk issues found - Review recommended before deployment.');
  } else {
    console.log('\n✅ No critical issues found. Security posture looks reasonable.');
  }
  
  return { findings, criticalCount, highCount, checkCount };
}

// Auto-fix function
async function runAutoFix() {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║                    AUTO-FIX MODE                            ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
  
  let fixedCount = 0;
  
  // Fix 1: Secure .env file
  const envFile = '/root/clawd/skills/.env';
  if (checkFileExists(envFile)) {
    try {
      const stats = fs.statSync(envFile);
      const mode = stats.mode & 0o777;
      if ((mode & 0o077) !== 0) {
        fs.chmodSync(envFile, 0o600);
        console.log('✅ Fixed: Set 600 permissions on .env');
        fixedCount++;
      }
    } catch (e) {
      console.log('❌ Failed to fix .env permissions:', e.message);
    }
  }
  
  // Fix 2: Secure other sensitive files
  const sensitivePatterns = [
    { pattern: /\.env$/, perms: 0o600 },
    { pattern: /\.json$/, perms: 0o600 },
    { pattern: /\.key$/, perms: 0o600 },
    { pattern: /\.pem$/, perms: 0o600 }
  ];
  
  const files = getFilesRecursively(CLAWDBOT_DIR);
  for (const file of files) {
    for (const sp of sensitivePatterns) {
      if (sp.pattern.test(file)) {
        try {
          const stats = fs.statSync(file);
          const mode = stats.mode & 0o777;
          if (mode !== sp.perms) {
            fs.chmodSync(file, sp.perms);
            console.log(`✅ Fixed: Set ${sp.perms.toString(8)} on ${path.basename(file)}`);
            fixedCount++;
          }
        } catch {
          // Ignore
        }
      }
    }
  }
  
  // Fix 3: Create .gitignore if missing
  const gitignorePath = path.join(CLAWDBOT_DIR, '.gitignore');
  if (!checkFileExists(gitignorePath)) {
    const defaultGitignore = `# Clawdbot
.env
*.log
node_modules/
.DS_Store
*.pem
*.key
`;
    fs.writeFileSync(gitignorePath, defaultGitignore);
    console.log('✅ Fixed: Created .gitignore');
    fixedCount++;
  }
  
  console.log(`\n✅ Auto-fix complete! ${fixedCount} issues resolved.`);
  
  // Re-run audit to confirm
  console.log('\n🔍 Re-running audit to verify...\n');
  return fixedCount;
}

// Run if called directly
if (require.main === module) {
  const args = process.argv.slice(2);
  
  const shouldFix = args.includes('--fix');
  
  if (shouldFix) {
    runAutoFix().catch(e => {
      console.error('Auto-fix error:', e.message);
      process.exit(1);
    });
  } else {
    runAudit({
      full: args.includes('--full'),
      json: args.includes('--json'),
      credentials: args.includes('--credentials'),
      ports: args.includes('--ports'),
      configs: args.includes('--configs'),
      permissions: args.includes('--permissions'),
      docker: args.includes('--docker')
    }).catch(e => {
      console.error('Audit error:', e.message);
      process.exit(1);
    });
  }
}

module.exports = { runAudit, checkCredentials, checkPorts, checkConfigs, checkPermissions, checkDocker };
