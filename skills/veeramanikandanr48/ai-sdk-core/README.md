# AI SDK Core

Backend AI with Vercel AI SDK v5/v6 - text generation, structured output, multi-modal (speech, transcription, image gen), embeddings, tools, and agents.

## Auto-Trigger Keywords

This skill should be discovered when working with:

### Primary Keywords (High Priority)
- ai sdk core, vercel ai sdk, ai sdk v5, ai sdk v6
- generateText, streamText, generate text ai
- Output.object, Output.array, Output.choice (v6)
- ai sdk node, ai sdk server, ai sdk backend
- zod ai schema, zod ai validation
- ai tools calling, ai agent class, agent with tools
- openai sdk, anthropic sdk, google gemini sdk
- multi-provider ai, ai provider switching

### v6 Output API Keywords (CRITICAL)
- Output API, Output.object, Output.array, Output.choice
- generateObject deprecated, streamObject deprecated
- ai sdk v6 migration, v6 breaking changes
- structured output v6, ai sdk structured data

### Multi-Modal Keywords
- ai sdk speech, generateSpeech, text to speech ai
- ai sdk transcription, transcribe audio, speech to text ai
- ai sdk image generation, generateImage, dall-e api
- ai sdk embeddings, embed, embedMany, cosineSimilarity
- multi-modal prompts, pdf ai, image ai, file ai

### Advanced Features Keywords
- ai sdk reranking, rerank documents, rag relevance
- ai sdk middleware, wrapLanguageModel, extractReasoningMiddleware
- ai sdk telemetry, opentelemetry ai, ai tracing
- ai sdk mcp, model context protocol, mcp tools
- tool approval, human in the loop ai, needsApproval

### Secondary Keywords (Medium Priority)
- ai streaming backend, stream ai responses
- ai server actions, nextjs ai server
- cloudflare workers ai sdk, workers-ai-provider
- ai sdk migration, v4 to v5 migration, v5 to v6 migration
- ai chat completion, llm text generation
- ai sdk typescript, typed ai responses
- stopWhen ai sdk, multi-step ai execution
- dynamic tools ai, runtime tools ai

### Error Keywords (Discovery on Errors)
- AI_APICallError, ai api call error
- AI_NoObjectGeneratedError, no object generated
- AI_LoadAPIKeyError, ai api key error
- AI_InvalidArgumentError, invalid argument ai
- AI_TypeValidationError, zod validation failed
- AI_RetryError, ai retry failed
- AI_NoSpeechGeneratedError, speech generation failed
- AI_NoTranscriptGeneratedError, transcription failed
- streamText fails silently, stream error swallowed
- worker startup limit ai sdk, 270ms startup
- ai rate limit, rate limiting ai
- maxTokens maxOutputTokens, v5 breaking changes
- providerMetadata providerOptions, tool inputSchema
- ToolExecutionError removed, tool-error parts

### Framework Keywords
- nextjs ai sdk, next.js server actions ai
- cloudflare workers ai integration
- node.js ai sdk, nodejs llm
- vercel ai deployment, serverless ai

### Provider Keywords
- openai integration, gpt-5 api, gpt-5.2 api, chatgpt api
- anthropic claude, claude api integration, claude 4 api
- google gemini api, gemini 2.5 integration
- cloudflare llama, workers ai llm
- elevenlabs ai sdk, deepgram ai sdk

## What This Skill Provides

- **v6 Output API**: Output.object/array/choice replaces deprecated generateObject/streamObject
- **Multi-Modal**: Speech synthesis, transcription, image generation, embeddings
- **Core Functions**: generateText, streamText with structured output
- **MCP Integration**: Model Context Protocol tools
- **Middleware**: Language model middleware patterns
- **Telemetry**: OpenTelemetry integration
- **Top Providers**: OpenAI, Anthropic, Google, Cloudflare, ElevenLabs, 60+ more
- **v4→v5 Migration**: Complete breaking changes guide
- **Top 12 Errors**: Common issues with solutions
- **Production Patterns**: Best practices for deployment

## Quick Links

- **Official Docs**: https://ai-sdk.dev/docs
- **Output API**: https://ai-sdk.dev/docs/ai-sdk-core/generating-structured-data
- **Multi-Modal**: https://ai-sdk.dev/docs/ai-sdk-core/speech
- **Migration Guide**: https://ai-sdk.dev/docs/migration-guides/migration-guide-5-0
- **Error Reference**: https://ai-sdk.dev/docs/reference/ai-sdk-errors
- **GitHub**: https://github.com/vercel/ai

## Installation

```bash
npm install ai @ai-sdk/openai @ai-sdk/anthropic @ai-sdk/google zod
```

## Usage

See `SKILL.md` for comprehensive documentation and examples.

## Version

- **Skill Version**: 2.0.0
- **AI SDK Version**: 6.1.0
- **Last Updated**: 2026-01-03

## Recent Updates (v2.0.0 - 2026-01-03)

- **BREAKING: Output API**: Added v6 Output.object/array/choice documentation (generateObject/streamObject deprecated)
- **Multi-Modal**: Added speech synthesis, transcription, image generation sections
- **Embeddings**: Added embed(), embedMany(), cosineSimilarity() with full examples
- **MCP Tools**: Added Model Context Protocol integration
- **Middleware**: Added wrapLanguageModel and extractReasoningMiddleware patterns
- **Telemetry**: Added OpenTelemetry integration
- **Models**: Added GPT-5.2, o3, o3-mini, o4-mini model references
- **Providers**: Updated to 69+ providers (was ~25)
- **Errors**: Updated to 31 error types (was 12 documented)

## Previous Updates (v1.2.0 - 2025-11-22)

- **v6 Beta**: Added AI SDK 6 beta features (Agent abstraction, tool approval, reranking)
- **Updated Models**: GPT-5.1, Claude Sonnet 4.5, Gemini 2.5 models

## License

MIT
