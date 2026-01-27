/**
 * Security Validator Hook - Pre-tool security validation
 * 
 * Automatically validates tool calls before execution to prevent:
 * - Command injection attacks
 * - SSRF (Server-Side Request Forgery)  
 * - Path traversal attempts
 * - Prompt injection
 * - API key exposure
 */

import { execSync } from 'child_process';
import { writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

interface ToolCallContext {
  tool: string;
  args: any;
  sessionKey?: string;
  userId?: string;
}

interface HookResult {
  allow?: boolean;
  error?: string;
  warning?: string;
  modified?: any;
}

// Configuration
const CONFIG = {
  strictMode: false,
  blockThreats: true,
  logEvents: true,
  securitySkillPath: join(homedir(), '.clawdbot', 'skills', 'security', 'security'),
  logFile: join(homedir(), '.clawdbot', 'logs', 'security-events.log')
};

// Ensure log directory exists
const logDir = join(homedir(), '.clawdbot', 'logs');
if (!existsSync(logDir)) {
  mkdirSync(logDir, { recursive: true });
}

// Logging function
function logSecurityEvent(level: string, message: string, context?: any) {
  if (!CONFIG.logEvents) return;
  
  const timestamp = new Date().toISOString();
  const logEntry = `${timestamp} [${level}] ${message}${context ? ` - Context: ${JSON.stringify(context)}` : ''}`;
  
  try {
    writeFileSync(CONFIG.logFile, logEntry + '\n', { flag: 'a' });
  } catch (error) {
    console.warn(`Failed to write security log: ${error}`);
  }
  
  // Also log to console for development
  const colorCode = {
    'THREAT': '\x1b[31m', // Red
    'SAFE': '\x1b[32m',   // Green
    'WARNING': '\x1b[33m', // Yellow
    'INFO': '\x1b[34m'    // Blue
  }[level] || '\x1b[0m';
  
  console.log(`${colorCode}[SECURITY-${level}]\x1b[0m ${message}`);
}

// Validate using security skill
function validateWithSecuritySkill(command: string, ...args: string[]): { allowed: boolean; reason?: string } {
  try {
    if (!existsSync(CONFIG.securitySkillPath)) {
      logSecurityEvent('WARNING', 'Security skill not found - validation skipped', { path: CONFIG.securitySkillPath });
      return { allowed: true }; // Fail-safe: allow if security skill unavailable
    }
    
    const fullCommand = `"${CONFIG.securitySkillPath}" ${command} ${args.map(arg => `"${arg}"`).join(' ')}`;
    const result = execSync(fullCommand, { encoding: 'utf8', timeout: 5000 });
    
    if (result.includes('ALLOWED') || result.includes('CLEAN') || result.includes('SAFE')) {
      return { allowed: true };
    } else if (result.includes('BLOCKED') || result.includes('FLAGGED') || result.includes('THREAT')) {
      const reasonMatch = result.match(/Pattern: ([^-]+)/);
      return { 
        allowed: false, 
        reason: reasonMatch ? reasonMatch[1].trim() : 'Security threat detected' 
      };
    }
    
    // If unclear result, allow but log warning
    logSecurityEvent('WARNING', 'Unclear security validation result', { command, result });
    return { allowed: true };
    
  } catch (error) {
    logSecurityEvent('WARNING', 'Security validation failed - allowing by default', { command, error: error.message });
    return { allowed: true }; // Fail-safe: allow on validation error
  }
}

/**
 * Before Tool Call Hook
 * Validates tool parameters before execution
 */
export async function before_tool_call(context: ToolCallContext): Promise<HookResult> {
  const { tool, args } = context;
  
  logSecurityEvent('INFO', `Validating tool call: ${tool}`, { args });
  
  try {
    switch (tool) {
      case 'bash':
      case 'exec':
        if (args.command) {
          const validation = validateWithSecuritySkill('validate-command', args.command);
          if (!validation.allowed) {
            logSecurityEvent('THREAT', `Command injection blocked - ${validation.reason}`, { 
              tool, 
              command: args.command 
            });
            
            if (CONFIG.blockThreats) {
              return {
                allow: false,
                error: `🔒 Security: Command blocked - ${validation.reason}. If this is legitimate, review security patterns or contact administrator.`
              };
            } else {
              return {
                allow: true,
                warning: `⚠️ Security: Potentially dangerous command detected - ${validation.reason}`
              };
            }
          }
          
          logSecurityEvent('SAFE', 'Command validated', { tool, command: args.command });
        }
        break;
        
      case 'web_fetch':
      case 'fetch':
        if (args.url) {
          const validation = validateWithSecuritySkill('check-url', args.url);
          if (!validation.allowed) {
            logSecurityEvent('THREAT', `SSRF attempt blocked - ${validation.reason}`, { 
              tool, 
              url: args.url 
            });
            
            if (CONFIG.blockThreats) {
              return {
                allow: false,
                error: `🔒 Security: URL blocked - ${validation.reason}. Potential SSRF or malicious site.`
              };
            } else {
              return {
                allow: true,
                warning: `⚠️ Security: Potentially dangerous URL detected - ${validation.reason}`
              };
            }
          }
          
          logSecurityEvent('SAFE', 'URL validated', { tool, url: args.url });
        }
        break;
        
      case 'read':
      case 'write':
      case 'edit':
        if (args.path || args.file_path || args.filePath) {
          const path = args.path || args.file_path || args.filePath;
          const validation = validateWithSecuritySkill('validate-path', path);
          if (!validation.allowed) {
            logSecurityEvent('THREAT', `Path traversal blocked - ${validation.reason}`, { 
              tool, 
              path 
            });
            
            if (CONFIG.blockThreats) {
              return {
                allow: false,
                error: `🔒 Security: Path blocked - ${validation.reason}. Potential path traversal or sensitive file access.`
              };
            } else {
              return {
                allow: true,
                warning: `⚠️ Security: Potentially dangerous path detected - ${validation.reason}`
              };
            }
          }
          
          logSecurityEvent('SAFE', 'Path validated', { tool, path });
        }
        break;
        
      default:
        // For other tools, scan any text content for prompt injection
        const textFields = ['content', 'text', 'message', 'query', 'prompt'];
        for (const field of textFields) {
          if (args[field] && typeof args[field] === 'string') {
            const validation = validateWithSecuritySkill('scan-content', args[field]);
            if (!validation.allowed) {
              logSecurityEvent('THREAT', `Prompt injection detected in ${field} - ${validation.reason}`, { 
                tool, 
                field,
                content: args[field].substring(0, 100) + '...' // Log first 100 chars only
              });
              
              if (CONFIG.strictMode) {
                return {
                  allow: false,
                  error: `🔒 Security: Content blocked - ${validation.reason}. Potential prompt injection detected.`
                };
              } else {
                return {
                  allow: true,
                  warning: `⚠️ Security: Suspicious content detected in ${field} - ${validation.reason}`
                };
              }
            }
          }
        }
        break;
    }
    
    return { allow: true };
    
  } catch (error) {
    logSecurityEvent('WARNING', 'Hook execution failed - allowing tool call', { 
      tool, 
      error: error.message 
    });
    return { allow: true }; // Fail-safe: allow on hook error
  }
}

/**
 * After Tool Call Hook  
 * Logs tool results for monitoring (doesn't block)
 */
export async function after_tool_call(context: ToolCallContext & { result?: any; error?: any }): Promise<HookResult> {
  const { tool, args, result, error } = context;
  
  try {
    if (error) {
      logSecurityEvent('INFO', `Tool failed: ${tool}`, { 
        args: typeof args === 'object' ? Object.keys(args) : args,
        error: error.message || error 
      });
    } else {
      logSecurityEvent('INFO', `Tool completed: ${tool}`, { 
        args: typeof args === 'object' ? Object.keys(args) : args,
        resultSize: typeof result === 'string' ? result.length : 'non-string'
      });
      
      // Scan tool results for accidentally exposed secrets
      if (result && typeof result === 'string') {
        const validation = validateWithSecuritySkill('scan-content', result.substring(0, 1000)); // First 1KB only
        if (!validation.allowed) {
          logSecurityEvent('WARNING', `Potential secrets in tool output - ${validation.reason}`, { 
            tool,
            outputSize: result.length
          });
        }
      }
    }
    
    return { allow: true };
    
  } catch (error) {
    logSecurityEvent('WARNING', 'After-tool hook failed', { tool, error: error.message });
    return { allow: true };
  }
}

// Export default for compatibility
export default {
  before_tool_call,
  after_tool_call
};