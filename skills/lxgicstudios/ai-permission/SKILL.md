---
name: permission-gen
description: Generate role-based permission systems
---

# Permission Generator

Describe your roles and resources, get a complete RBAC implementation.

## Quick Start

```bash
npx ai-permission "Admin, Editor, Viewer roles for posts and comments"
```

## What It Does

- Generates permission constants
- Creates role hierarchies
- Builds check functions
- Includes middleware

## Usage Examples

```bash
# Generate from description
npx ai-permission "Team admin, member, guest for projects and tasks"

# Generate with specific framework
npx ai-permission "roles for e-commerce" --framework express

# Output as module
npx ai-permission "admin system" --out ./src/lib/permissions.ts
```

## Output Includes

- Permission enum/constants
- Role definitions
- hasPermission() function
- Middleware for Express/Next.js
- TypeScript types

## Example Output

```typescript
export const Permissions = {
  POSTS_CREATE: 'posts:create',
  POSTS_READ: 'posts:read',
  POSTS_UPDATE: 'posts:update',
  POSTS_DELETE: 'posts:delete',
} as const;

export const Roles = {
  ADMIN: [Permissions.POSTS_CREATE, ...],
  EDITOR: [Permissions.POSTS_UPDATE, ...],
};
```

## Requirements

Node.js 18+. OPENAI_API_KEY required.

## License

MIT. Free forever.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-permission](https://github.com/lxgicstudios/ai-permission)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
