#!/usr/bin/env node

/**
 * Smart Follow-up Suggestions CLI
 * Generates contextual follow-up questions based on conversation history
 * 
 * Supports both direct Anthropic API and OpenRouter (Clawdbot's default)
 */

// Configuration
const DEFAULT_MODEL = 'anthropic/claude-sonnet-4.5'; // Same as Clawdbot primary model (OpenRouter format)
const MAX_TOKENS = 1024;
const OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1';

// Category definitions
const CATEGORIES = {
  QUICK: { emoji: '⚡', label: 'Quick', description: 'Clarifications and quick questions' },
  DEEP: { emoji: '🧠', label: 'Deep Dive', description: 'Technical exploration and detailed analysis' },
  RELATED: { emoji: '🔗', label: 'Related', description: 'Connected topics and broader context' }
};

/**
 * Parse conversation context from various input formats
 */
function parseContext(input) {
  if (typeof input === 'object' && input.exchanges) {
    return input.exchanges;
  }
  
  if (typeof input === 'string') {
    try {
      const parsed = JSON.parse(input);
      if (Array.isArray(parsed)) return parsed;
      if (parsed.exchanges) return parsed.exchanges;
    } catch (e) {
      // Not JSON, treat as plain text
      return [{ user: input, assistant: '' }];
    }
  }
  
  if (Array.isArray(input)) {
    return input;
  }
  
  throw new Error('Invalid context format. Expected array of exchanges or JSON string.');
}

/**
 * Build the prompt for generating follow-up suggestions
 */
function buildPrompt(exchanges) {
  const conversationText = exchanges.map((ex, i) => {
    return `Exchange ${i + 1}:\nUser: ${ex.user}\nAssistant: ${ex.assistant}`;
  }).join('\n\n');
  
  return `You are a helpful assistant generating smart follow-up suggestions for a conversation.

Based on the following conversation, generate exactly 3 follow-up questions in 3 categories:

**CATEGORIES:**
1. ⚡ Quick (1 question): Short clarification, definition, or immediate next step
2. 🧠 Deep Dive (1 question): Technical depth, advanced concept, or thorough exploration
3. 🔗 Related (1 question): Connected topic, broader context, or alternative perspective

**CONVERSATION:**
${conversationText}

**REQUIREMENTS:**
- Each question must be natural, conversational, and contextually relevant
- Vary the depth and style across categories
- Keep questions concise (max 80 characters each)
- Avoid yes/no questions when possible
- Make each question distinct and non-repetitive

**OUTPUT FORMAT (strict JSON):**
{
  "quick": "question text",
  "deep": "question text",
  "related": "question text"
}

Generate the follow-up suggestions now:`;
}

/**
 * Generate follow-up suggestions using OpenRouter API (or direct Anthropic)
 */
async function generateFollowups(exchanges, options = {}) {
  // Support both OPENROUTER_API_KEY and ANTHROPIC_API_KEY
  const apiKey = options.apiKey || process.env.OPENROUTER_API_KEY || process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('OPENROUTER_API_KEY or ANTHROPIC_API_KEY environment variable is required');
  }
  
  const isOpenRouter = apiKey.startsWith('sk-or-') || process.env.OPENROUTER_API_KEY;
  const prompt = buildPrompt(exchanges);
  const model = options.model || DEFAULT_MODEL;
  
  try {
    let text;
    
    if (isOpenRouter) {
      // Use OpenRouter API (OpenAI-compatible)
      const response = await fetch(`${OPENROUTER_BASE_URL}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://clawdbot.com',
          'X-Title': 'Smart Follow-ups Skill'
        },
        body: JSON.stringify({
          model: model,
          max_tokens: MAX_TOKENS,
          temperature: 0.7,
          messages: [{ role: 'user', content: prompt }]
        })
      });
      
      if (!response.ok) {
        const error = await response.text();
        throw new Error(`OpenRouter API error: ${response.status} - ${error}`);
      }
      
      const data = await response.json();
      text = data.choices[0].message.content.trim();
    } else {
      // Use direct Anthropic SDK
      const { Anthropic } = require('@anthropic-ai/sdk');
      const anthropic = new Anthropic({ apiKey });
      
      const response = await anthropic.messages.create({
        model: model.replace('anthropic/', ''), // Remove prefix for direct API
        max_tokens: MAX_TOKENS,
        temperature: 0.7,
        messages: [{ role: 'user', content: prompt }]
      });
      
      text = response.content[0].text.trim();
    }
    
    // Extract JSON from response (handle markdown code blocks)
    let jsonText = text;
    const jsonMatch = text.match(/```json\s*(\{[\s\S]*?\})\s*```/) || text.match(/(\{[\s\S]*\})/);
    if (jsonMatch) {
      jsonText = jsonMatch[1];
    }
    
    const suggestions = JSON.parse(jsonText);
    
    // Validate structure
    if (!suggestions.quick || !suggestions.deep || !suggestions.related) {
      throw new Error('Invalid suggestion structure from API');
    }
    
    // Ensure strings (not arrays for backward compatibility)
    return {
      quick: Array.isArray(suggestions.quick) ? suggestions.quick[0] : suggestions.quick,
      deep: Array.isArray(suggestions.deep) ? suggestions.deep[0] : suggestions.deep,
      related: Array.isArray(suggestions.related) ? suggestions.related[0] : suggestions.related
    };
    
  } catch (error) {
    if (error.name === 'SyntaxError') {
      throw new Error(`Failed to parse API response as JSON: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Format suggestions for different output modes
 */
function formatOutput(suggestions, mode = 'json') {
  switch (mode) {
    case 'json':
      return JSON.stringify(suggestions, null, 2);
    
    case 'telegram':
      // Telegram inline buttons format
      return JSON.stringify(createTelegramButtons(suggestions), null, 2);
    
    case 'text':
      return formatTextList(suggestions);
    
    case 'compact':
      return formatCompactList(suggestions);
    
    default:
      throw new Error(`Unknown output mode: ${mode}`);
  }
}

/**
 * Create Telegram inline button structure
 */
function createTelegramButtons(suggestions) {
  const buttons = [];
  
  // Row 1: Quick question
  buttons.push([{
    text: `${CATEGORIES.QUICK.emoji} ${suggestions.quick}`,
    callback_data: `ask:${suggestions.quick.substring(0, 50)}` // Truncate to fit 64-byte limit
  }]);
  
  // Row 2: Deep Dive question
  buttons.push([{
    text: `${CATEGORIES.DEEP.emoji} ${suggestions.deep}`,
    callback_data: `ask:${suggestions.deep.substring(0, 50)}`
  }]);
  
  // Row 3: Related question
  buttons.push([{
    text: `${CATEGORIES.RELATED.emoji} ${suggestions.related}`,
    callback_data: `ask:${suggestions.related.substring(0, 50)}`
  }]);
  
  return buttons;
}

/**
 * Format as numbered text list
 */
function formatTextList(suggestions) {
  let output = '💡 **Smart Follow-up Suggestions**\n\n';
  
  output += `${CATEGORIES.QUICK.emoji} **Quick**\n`;
  output += `1. ${suggestions.quick}\n`;
  
  output += `\n${CATEGORIES.DEEP.emoji} **Deep Dive**\n`;
  output += `2. ${suggestions.deep}\n`;
  
  output += `\n${CATEGORIES.RELATED.emoji} **Related**\n`;
  output += `3. ${suggestions.related}\n`;
  
  output += '\nReply with a number (1-3) to ask that question.';
  
  return output;
}

/**
 * Format as compact inline list
 */
function formatCompactList(suggestions) {
  const all = [
    `⚡ ${suggestions.quick}`,
    `🧠 ${suggestions.deep}`,
    `🔗 ${suggestions.related}`
  ];
  
  return all.map((q, i) => `${i + 1}. ${q}`).join('\n');
}

/**
 * CLI entry point
 */
async function main() {
  const args = process.argv.slice(2);
  
  // Parse CLI arguments
  const options = {
    mode: 'json',
    model: DEFAULT_MODEL,
    context: null
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--mode' || arg === '-m') {
      options.mode = args[++i];
    } else if (arg === '--model') {
      options.model = args[++i];
    } else if (arg === '--context' || arg === '-c') {
      options.context = args[++i];
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else if (!options.context) {
      // First positional arg is context
      options.context = arg;
    }
  }
  
  // Read from stdin if no context provided
  if (!options.context) {
    const chunks = [];
    for await (const chunk of process.stdin) {
      chunks.push(chunk);
    }
    options.context = Buffer.concat(chunks).toString('utf-8').trim();
  }
  
  if (!options.context) {
    console.error('Error: No conversation context provided');
    console.error('Usage: followups-cli [options] <context>');
    console.error('Run with --help for more information');
    process.exit(1);
  }
  
  try {
    // Parse and validate context
    const exchanges = parseContext(options.context);
    
    if (exchanges.length === 0) {
      throw new Error('No conversation exchanges found in context');
    }
    
    // Limit to last 3 exchanges
    const recentExchanges = exchanges.slice(-3);
    
    // Generate suggestions
    const suggestions = await generateFollowups(recentExchanges, options);
    
    // Format and output
    const output = formatOutput(suggestions, options.mode);
    console.log(output);
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

function printHelp() {
  console.log(`
Smart Follow-up Suggestions CLI

USAGE:
  followups-cli [options] <context>
  cat context.json | followups-cli [options]

OPTIONS:
  -c, --context <json>   Conversation context (JSON array or object)
  -m, --mode <mode>      Output mode: json|telegram|text|compact (default: json)
  --model <model>        Claude model to use (default: ${DEFAULT_MODEL})
  -h, --help             Show this help message

CONTEXT FORMAT:
  Array of exchanges: [{"user": "...", "assistant": "..."}, ...]
  Or object: {"exchanges": [...]}

OUTPUT MODES:
  json       - Raw JSON object with categories
  telegram   - Telegram inline buttons array
  text       - Numbered list with categories
  compact    - Simple numbered list

EXAMPLES:
  # From JSON file
  cat conversation.json | followups-cli --mode telegram

  # Direct input
  followups-cli --mode text '[{"user":"What is Docker?","assistant":"Docker is..."}]'

  # Custom model
  followups-cli --model claude-sonnet-4 --context context.json

ENVIRONMENT:
  OPENROUTER_API_KEY   Recommended: Your OpenRouter API key (Clawdbot default)
  ANTHROPIC_API_KEY    Alternative: Direct Anthropic API key
`);
}

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

// Export for use as library
module.exports = {
  generateFollowups,
  formatOutput,
  parseContext,
  CATEGORIES
};
