/**
 * Smart Follow-ups Handler
 * 
 * Integrates with Clawdbot to generate follow-up suggestions using
 * the current session's model and authentication.
 * 
 * Supports all Clawdbot channels with adaptive formatting:
 * - Buttons: Telegram, Discord, Slack
 * - Text: Signal, WhatsApp, iMessage, SMS, Matrix, Email
 */

// Channels with native button support
const BUTTON_CHANNELS = ['telegram', 'discord', 'slack'];

// Prompt for generating follow-ups
const FOLLOWUPS_PROMPT = `Based on our recent conversation, generate exactly 3 follow-up questions.

**Categories (one question each):**
1. ⚡ Quick — Short clarification or immediate next step (max 50 chars)
2. 🧠 Deep Dive — Technical depth or detailed exploration (max 50 chars)
3. 🔗 Related — Connected topic or broader context (max 50 chars)

**Rules:**
- Make questions natural and conversational
- Directly relevant to what we just discussed
- Avoid yes/no questions
- Keep each under 50 characters for button display

**Output format (strict JSON only, no markdown):**
{"quick":"question here","deep":"question here","related":"question here"}`;

/**
 * Check if channel supports inline buttons
 */
function supportsButtons(channel, capabilities = []) {
  return BUTTON_CHANNELS.includes(channel?.toLowerCase()) && 
         (capabilities.includes('inlineButtons') || capabilities.includes('buttons'));
}

/**
 * Parse follow-up suggestions from agent response
 */
function parseSuggestions(text) {
  try {
    // Try to extract JSON from response
    const jsonMatch = text.match(/\{[^{}]*"quick"[^{}]*"deep"[^{}]*"related"[^{}]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    
    // Fallback: try parsing entire response as JSON
    return JSON.parse(text.trim());
  } catch (e) {
    console.error('[smart-followups] Failed to parse suggestions:', e.message);
    return null;
  }
}

/**
 * Format suggestions as Telegram/Discord/Slack inline buttons
 */
function formatButtons(suggestions) {
  return [
    [{ text: `⚡ ${suggestions.quick}`, callback_data: suggestions.quick }],
    [{ text: `🧠 ${suggestions.deep}`, callback_data: suggestions.deep }],
    [{ text: `🔗 ${suggestions.related}`, callback_data: suggestions.related }]
  ];
}

/**
 * Format suggestions as text list (for channels without buttons)
 */
function formatTextList(suggestions, options = {}) {
  const { compact = false, stripEmoji = false } = options;
  
  if (compact) {
    // Minimal format for SMS
    let text = `Follow-ups:\n1. ${suggestions.quick}\n2. ${suggestions.deep}\n3. ${suggestions.related}\n\nReply 1, 2, or 3`;
    if (stripEmoji) {
      text = text.replace(/[⚡🧠🔗💡]/g, '');
    }
    return text;
  }
  
  // Full format with categories
  return `💡 **Smart Follow-up Suggestions**

⚡ **Quick**
1. ${suggestions.quick}

🧠 **Deep Dive**
2. ${suggestions.deep}

🔗 **Related**
3. ${suggestions.related}

Reply with 1, 2, or 3 to ask that question.`;
}

/**
 * Store suggestions in session for number reply handling
 */
function storeSuggestions(ctx, suggestions) {
  if (ctx.session) {
    ctx.session.lastFollowups = {
      '1': suggestions.quick,
      '2': suggestions.deep,
      '3': suggestions.related,
      timestamp: Date.now()
    };
  }
}

/**
 * Check if message is a follow-up number reply
 */
function isNumberReply(text) {
  return /^[123]$/.test(text?.trim());
}

/**
 * Get question from number reply
 */
function getQuestionFromNumber(ctx, number) {
  if (ctx.session?.lastFollowups) {
    const elapsed = Date.now() - ctx.session.lastFollowups.timestamp;
    // Only valid for 10 minutes
    if (elapsed < 10 * 60 * 1000) {
      return ctx.session.lastFollowups[number];
    }
  }
  return null;
}

/**
 * Skill module export
 */
module.exports = {
  name: 'smart-followups',
  version: '1.0.0',
  description: 'Generate contextual follow-up suggestions after AI responses',
  
  // Supported channels (all of them!)
  channels: ['telegram', 'discord', 'slack', 'signal', 'whatsapp', 'imessage', 'sms', 'matrix', 'email'],
  
  commands: {
    followups: {
      description: 'Generate 3 smart follow-up suggestions',
      aliases: ['fu', 'next', 'suggest'],
      
      /**
       * Handle /followups command
       */
      async execute(ctx) {
        const channel = ctx.channel?.toLowerCase() || 'unknown';
        const capabilities = ctx.capabilities || [];
        const useButtons = supportsButtons(channel, capabilities);
        
        // Return prompt that makes the agent generate follow-ups
        return {
          type: 'agent-prompt',
          prompt: FOLLOWUPS_PROMPT,
          
          // Post-process the agent's response
          transform: (response) => {
            const suggestions = parseSuggestions(response);
            
            if (!suggestions) {
              return {
                text: "Sorry, I couldn't generate follow-up suggestions. Try `/followups` again?"
              };
            }
            
            // Store for number reply handling (text mode)
            storeSuggestions(ctx, suggestions);
            
            if (useButtons) {
              return {
                text: '💡 **What would you like to explore next?**',
                buttons: formatButtons(suggestions)
              };
            } else {
              // Determine text format options based on channel
              const options = {
                compact: channel === 'sms',
                stripEmoji: channel === 'sms'
              };
              return {
                text: formatTextList(suggestions, options)
              };
            }
          }
        };
      }
    }
  },
  
  /**
   * Message interceptor for handling number replies
   */
  onMessage: async (ctx, next) => {
    const text = ctx.message?.text?.trim();
    
    // Check if this is a number reply to follow-ups
    if (isNumberReply(text)) {
      const question = getQuestionFromNumber(ctx, text);
      if (question) {
        // Replace the number with the actual question
        ctx.message.text = question;
        ctx.message._followupExpanded = true;
      }
    }
    
    return next();
  },
  
  // Export utilities for CLI/testing
  utils: {
    parseSuggestions,
    formatButtons,
    formatTextList,
    supportsButtons,
    FOLLOWUPS_PROMPT,
    BUTTON_CHANNELS
  }
};
