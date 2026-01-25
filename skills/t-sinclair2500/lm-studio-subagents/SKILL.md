---
name: lmstudio-subagents
description: "Equips agents to search for and offload tasks to local models in LM Studio. Use when: (1) Offloading simple tasks to free local models (summarization, extraction, classification, rewriting, first-pass code review, brainstorming), (2) Tasks need specialized model capabilities (vision models for images, smaller models for quick tasks, larger models for complex reasoning), (3) Saving paid API tokens by using local models when quality is sufficient, (4) Tasks require local-only processing or privacy. Requires LM Studio installed with lms CLI and server running."
metadata: {"clawdbot":{"emoji":"🦞","requires":{"bins":["lms"]},"tags":["local-model","local-llm","lm-studio","privacy","subagents"]}}
license: MIT
---

# LM Studio Local Models

Use **LM Studio** local models directly via API calls to offload tasks to free, local AI models. This skill equips agents to discover available models, select appropriate ones based on task requirements, and use them for cost-effective local processing without requiring pre-configuration in Clawdbot.

## Why this skill exists (when to reach for it)

Use this skill to **offload self-contained work to local/free models** when quality is sufficient—saving paid tokens for tasks that truly need your primary model.

Great fits:
- Summarization, extraction, classification, rewriting
- “First-pass” code review or refactoring suggestions
- Drafting outlines, alternatives, and brainstorming

Avoid / be cautious:
- Tasks requiring web access, proprietary tools, or high-stakes correctness (use your primary model)

## Key Terms

- **model_key**: The identifier used by `lms` commands (from `lms ls`). This is what you pass to `lms load`.
- **model_identifier**: The identifier used when loading with `--identifier`. Can be the same as `model_key` or a custom name. This is what you use in API calls to LM Studio.
- **lm_studio_api_url**: The base URL for LM Studio's API. Default is `http://127.0.0.1:1234/v1`. No Clawdbot config required - the skill works with LM Studio's default server.

**Note:** The description above contains all triggering information. The sections below provide implementation details for using the skill once triggered.

## Prerequisites

- LM Studio installed with `lms` CLI available on PATH
- LM Studio server running (default: http://127.0.0.1:1234)
- Models downloaded in LM Studio
- Node.js available (for helper script; curl can be used as alternative)

## Complete Workflow

### Step 0: Preflight (Required)

1) Verify LM Studio CLI is available:

```bash
exec command:"lms --help"
```

2) Verify the LM Studio server is running and reachable:

```bash
exec command:"lms server status --json"
```

### Step 1: List Available Models

Get all downloaded models:

```bash
exec command:"lms ls --json"
```

Parse JSON to extract:
- model_key (e.g., `meta-llama-3.1-8b-instruct` or `lmstudio-community/meta-llama-3.1-8b-instruct`)
- Type (llm, vlm, embeddings)
- Size (disk space)
- Architecture (Llama, Qwen2, etc.)
- Parameters (model size)

Filter by type if needed:
- `lms ls --json --llm` - Only LLM models
- `lms ls --json --embedding` - Only embedding models
- `lms ls --json --detailed` - More detailed information

### Step 2: Check Currently Loaded Models

Check what's already in memory:

```bash
exec command:"lms ps --json"
```

Parse JSON to see which models are currently loaded.

If a suitable model is already loaded (check by model_identifier), skip to Step 6 (call API).

### Step 3: Model Selection

Analyze task requirements and select appropriate model:

**Selection Criteria:**
- **Task complexity**: Smaller models (1B-3B) for simple tasks, larger models (7B+) for complex tasks
- **Context requirements**: Match model's max context length to task needs
- **Model capabilities**: VLM models for vision tasks, embeddings for search, LLMs for text generation
- **Memory constraints**: Prefer already-loaded models when appropriate
- **Model size**: Balance capability needs with available memory

**Model Selection:**
- Pick a `model_key` from `lms ls` that matches task requirements.
- Use the `model_key` as the `model_identifier` when loading (or derive a clean identifier from it).
- Any model in LM Studio can be used - no configuration needed.

### Step 4: Load Model

Before loading a large model, optionally estimate memory needs:

```bash
exec command:"lms load --estimate-only <model_key>"
```

Load the selected model into memory:

```bash
exec command:"lms load <model_key> --identifier \"<model_identifier>\" --ttl 3600"
```

**Optional flags:**
- `--gpu=max|auto|0.0-1.0` - Control GPU offload (e.g., `--gpu=0.5` for 50% GPU, `--gpu=max` for full GPU)
- `--context-length=<N>` - Set context length (e.g., `--context-length=4096`)
- `--identifier="<name>"` - Assign custom identifier for API reference (use model_key or derive clean identifier)
- `--ttl=<seconds>` - Auto-unload after inactivity period (recommended default to avoid thrash and cleanup races)

**Important**: The `lms load` command blocks until the model is fully loaded. For large models (70B+), this can take 3+ minutes. The command will return when loading completes.

**Example:**
```bash
exec command:"lms load meta-llama-3.1-8b-instruct --identifier \"meta-llama-3.1-8b-instruct\" --gpu=auto --context-length=4096 --ttl 3600"
```

### Step 5: Verify Model Loaded (CRITICAL SAFETY STEP)

**NEVER call the API without verifying the model is loaded.**

**Note**: Since `lms load` blocks until loading completes, verification should be straightforward. However, verify anyway as a safety check.

Verify the model is actually in memory:

```bash
exec command:"lms ps --json"
```

Parse JSON response and check if model_identifier appears as a loaded identifier.

**If model not found:**
1. This should be rare since `lms load` blocks until complete, but if it happens:
2. Wait 2-3 seconds (model may still be finalizing)
3. Retry verification: `exec command:"lms ps --json"`
4. Repeat up to 3 attempts total
5. If still not loaded after retries: **ABORT** with error message, do NOT call API

**If model found:** Proceed to call LM Studio API.

### Step 6: Call LM Studio API Directly

Call LM Studio's OpenAI-compatible API directly using the loaded model.

**Option A: Using helper script (recommended for reliability)**

```bash
exec command:"node {baseDir}/scripts/lmstudio-api.mjs <model_identifier> '<task description>' --temperature=0.7 --max-tokens=2000"
```

The script handles:
- Proper JSON encoding (no escaping issues)
- Error handling and retries
- Response validation (checks `response.model` matches request)
- Consistent output format

**Option B: Direct curl call**

**API URL:** Use default `http://127.0.0.1:1234/v1` (LM Studio's standard default). No configuration needed.

**Make API call:**

```bash
exec command:"curl -X POST <lm_studio_api_url>/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer lmstudio' \
  -d '{
    \"model\": \"<model_identifier>\",
    \"messages\": [{\"role\": \"user\", \"content\": \"<task description>\"}],
    \"temperature\": 0.7,
    \"max_tokens\": 2000
  }'"
```

**Parameters:**
- `model` (required): The model_identifier used when loading (must match `--identifier` from Step 4)
- `messages` (required): Array of message objects with `role` and `content`
- `temperature` (optional): Sampling temperature (0.0-2.0, default 0.7)
- `max_tokens` (optional): Maximum tokens to generate (adjust based on task)

**Response format:**
- Parse JSON response
- **Validate `response.model` field matches requested model_identifier** (LM Studio may use different model if requested one isn't loaded)
- Extract `choices[0].message.content` for the model's response
- Check for `error` field in response for error handling

**Example (using script):**
```bash
exec command:"node {baseDir}/scripts/lmstudio-api.mjs meta-llama-3.1-8b-instruct 'Summarize this document and extract key points' --temperature=0.7 --max-tokens=2000"
```

**Example (using curl):**
```bash
exec command:"curl -X POST http://127.0.0.1:1234/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer lmstudio' \
  -d '{
    \"model\": \"meta-llama-3.1-8b-instruct\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Summarize this document and extract key points\"}],
    \"temperature\": 0.7,
    \"max_tokens\": 2000
  }'"
```

### Step 7: Format and Return Results

Extract and format the API response:

**If using helper script:**
1. Parse JSON output from script (already validated)
2. Extract `content` field - this contains the model's response
3. Optionally use `usage` field for token statistics
4. Format the result appropriately for the task context
5. Return the formatted result to the user

**If using curl directly:**
1. Parse the JSON response from the curl command
2. **Validate `response.model` field** - ensure it matches the requested `model_identifier` (important: LM Studio may auto-select models)
3. Extract `choices[0].message.content` - this contains the model's response
4. Check for errors: if response contains `error` field, handle appropriately
5. If `response.model` doesn't match request, log warning but proceed (LM Studio behavior)
6. Format the result appropriately for the task context
7. Return the formatted result to the user

**Error handling:**
- If `error` field present: report error message to user
- If `response.model` doesn't match: log warning, proceed with response (LM Studio may have auto-selected model)
- If response structure unexpected: log warning and attempt to extract content
- If API call fails (non-200 status): report HTTP error

### Step 8: Unload Model (Cleanup)

**Default policy**: Rely on `--ttl` for automatic cleanup to avoid thrash and races. Unload explicitly when you hit memory pressure or the user requests immediate cleanup.

If unloading explicitly after API call completes:

```bash
exec command:"lms unload <model_identifier>"
```

**Note**: `lms unload` accepts either the model_key or the identifier. Since we loaded with `--identifier`, use the model_identifier for consistency.

**Handle errors gracefully:**
- If model already unloaded: No-op, continue
- If model still in use: Log warning, suggest manual cleanup later
- If unload fails: Log warning, suggest manual cleanup

## Model Selection Guide

### Decision inputs (what to look at)

Pull these from `lms ls --json` (and optionally `lms ls --json --detailed`):
- `type`: `llm` | `vlm` | `embedding`
- `vision`: boolean (if the task includes images, require `vision=true`)
- `trainedForToolUse`: boolean (prefer true when tool/function calling is important)
- `maxContextLength`: number (require enough context for long docs)
- `paramsString` / model size: rough proxy for cost/speed

Also check runtime state:
- `lms ps --json` for already-loaded candidates (prefer these to avoid load time and memory churn)

### Heuristics (simple selection policy)

Use a constraints-first approach, then score:

1) **Hard constraints**
- If the task is vision/image-based → only consider models where `vision=true`
- If you need embeddings → only consider `type=embedding`
- If task requires a minimum context window → only consider models with `maxContextLength >= needed`

2) **Preferences / scoring**
- Prefer models already loaded (`lms ps`) if they meet constraints
- Prefer `trainedForToolUse=true` when the task benefits from structured tool use
- Prefer smaller models for cheap/fast tasks; larger models for deeper reasoning

3) **Fallbacks**
- If no model meets constraints: either pick the closest match (and warn) or fall back to your primary model.

### Memory optimization

- Check `lms ps` first — prefer already-loaded models when appropriate
- Use `lms load --estimate-only <model_key>` to preview requirements
- Use `--ttl` to avoid leaving large models resident indefinitely

## Safety Checks

### CRITICAL: Load Verification

**Never call the API without verifying the model is loaded.**

The verification step (Step 5) is mandatory. Without it:
- API call may fail with "model not available" errors
- Wasted resources making API calls that can't succeed
- Confusing error messages

### Retry Logic

Load verification includes retry logic to handle eventual consistency:
1. Initial check immediately after load
2. Wait 2-3 seconds if not found
3. Retry up to 3 total attempts
4. Abort if still not loaded after retries

### Model Identifier Consistency

Ensure consistent use of model identifiers:
- Use `model_key` from `lms ls` for `lms load`
- Use the same `model_identifier` (from `--identifier`) for API calls
- The identifier used in API calls must match what was loaded

## Error Handling

### Model Not Found

**Symptom:** `lms ls` doesn't show the model, or `lms load` fails with "model not found"

**Response:**
- Error message: "Model <model-key> not found in LM Studio"
- Suggest: "Download the model first using `lms get <model-key>` or via LM Studio UI"

### API Call Failed

**Symptom:** curl command returns non-200 status or error response

**Response:**
- Check HTTP status code in response
- If 404: Model not found or not loaded - verify model_identifier matches loaded model
- If 500: LM Studio server error - check server logs, try reloading model
- If connection refused: LM Studio server not running - start server first
- Extract error message from response JSON if available
- Suggest: "Verify model is loaded with `lms ps`, check LM Studio server status, or try reloading the model"

### Invalid API Response

**Symptom:** API call succeeds but response structure is unexpected or missing content

**Response:**
- Check if response contains `choices` array
- Check if `choices[0].message.content` exists
- If structure unexpected: Log warning, attempt to extract any available content
- If completely malformed: Report error and suggest retrying the API call

### Load Timeout

**Symptom:** `lms load` command hangs or takes extremely long

**Response:**
- `lms load` blocks until loading completes, which can take 3+ minutes for large models (70B+)
- The exec tool has a default timeout (1800 seconds / 30 minutes) which should be sufficient
- If timeout occurs: "Model load timed out - this may indicate insufficient memory or a corrupted model file"
- Suggest: "Try smaller model, free up memory by unloading other models, or verify model file integrity"

### Load Verification Fails

**Symptom:** Load command succeeds but `lms ps` doesn't show model after retries

**Response:**
- This should be rare since `lms load` blocks until complete
- If it happens: Abort workflow with error: "Model failed to appear after load completion"
- Do NOT call API
- Suggest: "Check LM Studio logs, verify the identifier matches what was loaded, try reloading"

### Insufficient Memory

**Symptom:** `lms load` fails with memory-related errors

**Response:**
- Error message: "Insufficient memory to load model"
- Suggest: "Unload other models using `lms unload --all` or select smaller model"
- Use `lms load --estimate-only` to preview requirements

### API Call Fails After Verification

**Symptom:** Model verified as loaded but API call fails

**Response:**
- Report error to user
- Check if model is still loaded: `lms ps --json`
- If model disappeared: Reload model and retry API call
- If model still loaded but API fails: Check API URL, verify model_identifier matches exactly
- Still attempt to unload model (cleanup) if requested

### Model Already Loaded

**Symptom:** `lms ps` shows model is already loaded

**Response:**
- Skip load step (Step 4)
- Proceed directly to verification (Step 5) and then API call (Step 6)
- This is an optimization, not an error
- Ensure the model_identifier matches what's already loaded

### Unload Fails

**Symptom:** `lms unload` fails (model still in use, etc.)

**Response:**
- Log warning: "Failed to unload model <model-key>"
- Suggest: "Model may still be in use, unload manually later with `lms unload <model-key>`"
- Continue workflow (unload failure doesn't block completion)

## Examples

### Simple Task: Document Summarization

```bash
# 1. List models
exec command:"lms ls --json --llm"

# 2. Check loaded
exec command:"lms ps --json"

# 3. Select small model (e.g., meta-llama-3.1-8b-instruct)

# 4. Load model
exec command:"lms load meta-llama-3.1-8b-instruct --identifier \"meta-llama-3.1-8b-instruct\" --ttl 3600"

# 5. Verify loaded
exec command:"lms ps --json"
# Parse and confirm model appears

# 6. Call LM Studio API (using helper script)
exec command:"node {baseDir}/scripts/lmstudio-api.mjs meta-llama-3.1-8b-instruct 'Summarize this document and extract 5 key points' --temperature=0.7 --max-tokens=2000"

# 7. Parse response and extract content field

# 8. Optional explicit unload after completion (otherwise rely on TTL)
exec command:"lms unload meta-llama-3.1-8b-instruct"
```

### Complex Task: Codebase Analysis

```bash
# 1-2. List and check (same as above)

# 3. Select larger model (e.g., meta-llama-3.1-70b-instruct)

# 4. Load with context length
exec command:"lms load meta-llama-3.1-70b-instruct --identifier \"meta-llama-3.1-70b-instruct\" --context-length=8192 --gpu=auto --ttl 3600"

# 5. Verify loaded
exec command:"lms ps --json"

# 6. Call LM Studio API with longer context (using helper script)
exec command:"node {baseDir}/scripts/lmstudio-api.mjs meta-llama-3.1-70b-instruct 'Analyze the codebase architecture, identify main components, and suggest improvements' --temperature=0.3 --max-tokens=4000"

# 7. Parse response and format results

# 8. Optional unload (same as above)
```

### Vision Task: Image Description

```bash
# 1. List VLM models
exec command:"lms ls --json"

# 2-3. Select VLM model (e.g., qwen2-vl-7b-instruct)

# 4. Load VLM model
exec command:"lms load qwen2-vl-7b-instruct --identifier \"qwen2-vl-7b-instruct\" --gpu=max --ttl 3600"

# 5. Verify loaded
exec command:"lms ps --json"

# 6. Call LM Studio API with image (if supported by model, using helper script)
exec command:"node {baseDir}/scripts/lmstudio-api.mjs qwen2-vl-7b-instruct 'Describe this image in detail, including objects, colors, composition, and any text visible' --temperature=0.7 --max-tokens=2000"

# 7-8. Parse response and unload
```

## LM Studio API Details

### Helper Script (Recommended)

The skill includes `scripts/lmstudio-api.mjs` for reliable API calls. This script is optional but recommended for better error handling and response validation.

**Benefits:**
- Proper JSON encoding (no escaping issues)
- Built-in error handling
- Response validation (checks `response.model` matches request)
- Consistent output format
- Environment variable support (`LM_STUDIO_API_URL`)

**Usage:**
```bash
node {baseDir}/scripts/lmstudio-api.mjs <model_identifier> '<task>' [--temperature=0.7] [--max-tokens=2000] [--api-url=http://127.0.0.1:1234/v1]
```

**Output:**
```json
{
  "content": "<model response>",
  "model": "<model used>",
  "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
}
```

**Note:** If Node.js is not available, you can use curl directly (see Option B in Step 6).

### API Endpoint Format

LM Studio exposes an OpenAI-compatible API endpoint:
- Base URL: `http://127.0.0.1:1234/v1` (default, no configuration required)
- Chat completions: `POST /v1/chat/completions`
- Models list: `GET /v1/models`

### Determining API URL

The API URL defaults to `http://127.0.0.1:1234/v1` (LM Studio's standard default). **No configuration is required** - the skill works out of the box with LM Studio's default server.

The helper script supports `LM_STUDIO_API_URL` environment variable if you need to override the default URL.

### Request Format (OpenAI-Compatible)

```json
{
  "model": "<model_identifier>",
  "messages": [
    {"role": "user", "content": "<task description>"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Required fields:**
- `model`: Must match the identifier used when loading (`--identifier` value)
- `messages`: Array of message objects with `role` ("user", "assistant", "system") and `content`

**Optional fields:**
- `temperature`: 0.0-2.0 (default 0.7)
- `max_tokens`: Maximum tokens to generate
- `stream`: `true` for streaming responses (not recommended for exec tool)
- `top_p`: Nucleus sampling parameter
- `frequency_penalty`: -2.0 to 2.0
- `presence_penalty`: -2.0 to 2.0

### Response Format

**Success response:**
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "<model_identifier>",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "<model response>"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "total_tokens": 300
  }
}
```

**Error response:**
```json
{
  "error": {
    "message": "Error description",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

### Response Parsing

1. Parse JSON response from curl command
2. Check for `error` field - if present, handle error
3. **Validate `response.model` field** - ensure it matches the requested `model_identifier` (LM Studio may use a different model if the requested one isn't loaded)
4. Extract `choices[0].message.content` for the model's response
5. Optionally extract `usage` for token statistics
6. Format and return content to user

**Important:** Always validate `response.model` matches the requested model. LM Studio may auto-select/auto-load models, so the API may succeed even if `lms ps` doesn't show your requested model. If `response.model` doesn't match, log a warning or handle appropriately.

### Authentication

LM Studio API typically uses:
- Header: `Authorization: Bearer lmstudio`
- Some setups may not require authentication (check LM Studio server settings)

## Notes

- **Model identifier**: Use the same identifier for `--identifier` when loading and `model` in API calls
- **JSON output**: Always use `--json` flag for `lms` commands for machine-readable output
- **Already loaded**: Check `lms ps` first - if model is already loaded, skip load step to save time
- **Cleanup policy**: Prefer `--ttl` to avoid thrash; explicitly unload on memory pressure or when requested
- **No config required**: Models do not need to be pre-configured in Clawdbot - any model in LM Studio can be used
- **Load time**: `lms load` blocks until complete. Large models (70B+) can take 3+ minutes. This is normal and expected
- **API compatibility**: LM Studio uses OpenAI-compatible API format, so standard OpenAI request/response patterns apply
- **Model validation**: Always validate `response.model` field matches requested model_identifier. LM Studio may auto-select/auto-load models, so API calls may succeed even if `lms ps` doesn't show the requested model
- **Model name validation**: LM Studio API may not reject unknown model names - it may use whatever model is currently loaded. Always validate model exists via `lms ls` before making API calls
- **Tested with**: LM Studio version 0.3.39. Behavior may vary with different versions