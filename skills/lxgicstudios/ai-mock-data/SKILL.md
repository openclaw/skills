---
name: mock-data
description: Generate realistic mock data from TypeScript types
---

# Mock Data Generator

Give it your types, get realistic fake data. Perfect for tests and development.

## Quick Start

```bash
npx ai-mock-data ./src/types/User.ts
```

## What It Does

- Reads TypeScript interfaces
- Generates realistic fake data
- Understands field names (email, phone, etc.)
- Creates arrays with varied data

## Usage Examples

```bash
# Generate from type file
npx ai-mock-data ./src/types/Order.ts

# Generate specific count
npx ai-mock-data ./types/User.ts --count 50

# Output as JSON file
npx ai-mock-data ./types/Product.ts --out ./fixtures/products.json

# Generate for specific type
npx ai-mock-data ./types/index.ts --type Customer
```

## Output Example

```json
[
  {
    "id": "usr_8x7k2m",
    "email": "sarah.chen@gmail.com",
    "name": "Sarah Chen",
    "createdAt": "2024-01-15T09:23:00Z"
  }
]
```

## Smart Field Detection

- `email` → realistic emails
- `phone` → formatted phone numbers
- `address` → real-looking addresses
- `price` → appropriate currency values

## Requirements

Node.js 18+. OPENAI_API_KEY required.

## License

MIT. Free forever.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-mock-data](https://github.com/lxgicstudios/ai-mock-data)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
