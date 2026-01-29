---
name: snapshot-test
description: Generate Jest snapshot tests for components
---

# Snapshot Test Generator

Point it at your components, get snapshot tests. Covers common states and props.

## Quick Start

```bash
npx ai-snapshot-test ./src/components/Button.tsx
```

## What It Does

- Generates Jest snapshot tests
- Covers default and edge cases
- Tests different prop combinations
- Handles async components

## Usage Examples

```bash
# Generate for a component
npx ai-snapshot-test ./src/components/Card.tsx

# Generate for directory
npx ai-snapshot-test ./src/components/

# With specific test runner
npx ai-snapshot-test ./components --runner vitest
```

## Output Example

```typescript
describe('Button', () => {
  it('renders default state', () => {
    const { container } = render(<Button>Click me</Button>);
    expect(container).toMatchSnapshot();
  });

  it('renders disabled state', () => {
    const { container } = render(<Button disabled>Click me</Button>);
    expect(container).toMatchSnapshot();
  });
});
```

## Test Cases Generated

- Default props
- Required prop variations
- Edge cases (empty, null)
- Loading/error states
- Different sizes/variants

## Requirements

Node.js 18+. OPENAI_API_KEY required.

## License

MIT. Free forever.
