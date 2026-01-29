# ai-snapshot-test

Auto-generate Jest snapshot tests for your React components. Covers all prop variations and edge cases.

## Install

```bash
npm install -g ai-snapshot-test
```

## Usage

```bash
npx ai-snapshot-test ./src/components/Button.tsx
# → Generated ./src/components/Button.snap.test.tsx

npx ai-snapshot-test "./src/components/*.tsx"
# → Generates tests for all components
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
