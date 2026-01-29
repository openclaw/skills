# ai-api-docs

Generate API documentation from your route files. Supports markdown and OpenAPI output.

## Install

```bash
npm install -g ai-api-docs
```

## Usage

```bash
npx ai-api-docs ./src/routes/
# → API docs written to API_DOCS.md

npx ai-api-docs ./src/routes/ --format openapi -o spec.yaml
# → OpenAPI 3.0 spec

npx ai-api-docs ./src/api/ -o docs/api.md
# → Custom output path
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
