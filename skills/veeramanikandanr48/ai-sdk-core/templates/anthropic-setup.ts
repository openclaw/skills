// Anthropic provider configuration
// AI SDK Core - Anthropic (Claude) setup and usage

import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

async function main() {
  console.log('=== Anthropic (Claude) Provider Setup ===\n');

  // Method 1: Use environment variable (recommended)
  // ANTHROPIC_API_KEY=sk-ant-...
  const model1 = anthropic('claude-sonnet-4-5');

  // Method 2: Explicit API key
  const model2 = anthropic('claude-sonnet-4-5', {
    apiKey: process.env.ANTHROPIC_API_KEY,
  });

  // Available models (Claude 4.x family - current)
  const models = {
    sonnet45: anthropic('claude-sonnet-4-5'),  // Latest, recommended
    opus4: anthropic('claude-opus-4-0'),       // Highest intelligence
    haiku45: anthropic('claude-haiku-4-5'),    // Fastest
  };

  // Legacy models (Claude 3.x - deprecated, use Claude 4.x instead)
  // const legacyModels = {
  //   sonnet35: anthropic('claude-3-5-sonnet-20241022'),
  //   opus3: anthropic('claude-3-opus-20240229'),
  //   haiku3: anthropic('claude-3-haiku-20240307'),
  // };

  // Example: Generate text with Claude
  console.log('Generating text with Claude Sonnet 4.5...\n');

  const result = await generateText({
    model: models.sonnet45,
    prompt: 'Explain what makes Claude different from other AI assistants in 2 sentences.',
    maxOutputTokens: 150,
  });

  console.log('Response:', result.text);
  console.log('\nUsage:');
  console.log('- Prompt tokens:', result.usage.promptTokens);
  console.log('- Completion tokens:', result.usage.completionTokens);
  console.log('- Total tokens:', result.usage.totalTokens);

  // Example: Long context handling
  console.log('\n=== Long Context Example ===\n');

  const longContextResult = await generateText({
    model: models.sonnet45,
    messages: [
      {
        role: 'user',
        content: 'I will give you a long document to analyze. Here it is: ' + 'Lorem ipsum '.repeat(1000),
      },
      {
        role: 'user',
        content: 'Now summarize the key points.',
      },
    ],
    maxOutputTokens: 200,
  });

  console.log('Long context summary:', longContextResult.text);

  // Model selection guide
  console.log('\n=== Model Selection Guide ===');
  console.log('- Claude Sonnet 4.5: Latest model, best balance (recommended)');
  console.log('- Claude Opus 4.0: Highest intelligence for complex reasoning');
  console.log('- Claude Haiku 4.5: Fastest and most cost-effective');
  console.log('\nAll Claude 4.x models support extended context windows');
  console.log('Note: Claude 3.x models deprecated in 2025, use Claude 4.x instead');
}

main().catch(console.error);
