#!/usr/bin/env node

/**
 * LM Studio API Call Helper
 * 
 * Makes API calls to LM Studio and handles response validation.
 * Usage: node scripts/lmstudio-api.mjs <model_identifier> <task_content> [options]
 */

const BASE_URL = process.env.LM_STUDIO_API_URL || 'http://127.0.0.1:1234/v1';

async function callLMStudioAPI(modelIdentifier, taskContent, options = {}) {
  const {
    temperature = 0.7,
    maxTokens = 2000,
    apiUrl = BASE_URL
  } = options;

  const url = `${apiUrl}/chat/completions`;
  const payload = {
    model: modelIdentifier,
    messages: [{ role: 'user', content: taskContent }],
    temperature: parseFloat(temperature),
    max_tokens: parseInt(maxTokens)
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer lmstudio'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.error?.message || `HTTP ${response.status}`;
      console.error(JSON.stringify({ error: errorMsg, type: data.error?.type || 'api_error' }));
      process.exit(1);
    }

    // Validate response.model matches request
    if (data.model && data.model !== modelIdentifier) {
      console.warn(`Warning: Requested model "${modelIdentifier}" but got "${data.model}"`);
    }

    // Extract content
    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
      console.error(JSON.stringify({ error: 'Invalid API response structure', data }));
      process.exit(1);
    }

    const content = data.choices[0].message.content;
    const result = {
      content,
      model: data.model || modelIdentifier,
      usage: data.usage || null
    };

    console.log(JSON.stringify(result));
    return result;

  } catch (error) {
    console.error(JSON.stringify({ 
      error: error.message, 
      type: 'network_error',
      url 
    }));
    process.exit(1);
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const [modelIdentifier, taskContent, ...args] = process.argv.slice(2);
  
  if (!modelIdentifier || !taskContent) {
    console.error('Usage: node scripts/lmstudio-api.mjs <model_identifier> <task_content> [--temperature=0.7] [--max-tokens=2000] [--api-url=http://127.0.0.1:1234/v1]');
    process.exit(1);
  }

  const options = {};
  args.forEach(arg => {
    if (arg.startsWith('--temperature=')) {
      options.temperature = arg.split('=')[1];
    } else if (arg.startsWith('--max-tokens=')) {
      options.maxTokens = arg.split('=')[1];
    } else if (arg.startsWith('--api-url=')) {
      options.apiUrl = arg.split('=')[1];
    }
  });

  callLMStudioAPI(modelIdentifier, taskContent, options).catch(err => {
    console.error(JSON.stringify({ error: err.message, type: 'unexpected_error' }));
    process.exit(1);
  });
}

export { callLMStudioAPI };
