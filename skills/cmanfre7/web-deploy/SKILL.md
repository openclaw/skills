# web-deploy

Build and deploy websites, web apps, and APIs to production.

## Local Preview Workflow

```bash
# Static site
npx http-server ./dist -p 8080 -c-1

# Next.js
npm run dev          # Development (hot reload)
npm run build && npm run start  # Production preview

# FastAPI
uvicorn app.main:app --reload --port 8000

# Vite-based
npm run dev          # Dev server
npm run build && npx serve dist  # Production preview
```

## Deployment Targets

### Vercel (Frontend / Next.js / Static)

```bash
# First time setup
npx vercel link

# Preview deployment
npx vercel

# Production deployment
npx vercel --prod

# Environment variables
npx vercel env add SECRET_KEY
```

**Best for:** Next.js apps, React SPAs, static sites, serverless functions.

**Config:** `vercel.json` (usually not needed for Next.js)
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "nextjs"
}
```

### Railway (Backend / APIs / Databases)

```bash
# First time setup
railway login
railway init

# Deploy
railway up

# Add database
railway add --plugin postgresql

# Environment variables
railway variables set SECRET_KEY=value

# View logs
railway logs
```

**Best for:** Backend APIs, databases, long-running processes, Docker containers.

### GitHub Pages (Static Sites)

```bash
# Using gh-pages package
npm install -D gh-pages
# Add to package.json scripts: "deploy": "gh-pages -d dist"
npm run build && npm run deploy
```

**Best for:** Documentation, simple static sites, project pages.

### Canvas (Clawdbot Workspace)

Deploy to `~/clawd/canvas/` for local serving through the clawdbot gateway.
```bash
cp -r ./dist/* ~/clawd/canvas/my-project/
```

## Pre-Deploy Checklist

- [ ] Build succeeds locally (`npm run build` / `python -m build`)
- [ ] No TypeScript/lint errors
- [ ] Tests pass
- [ ] Environment variables set on target platform
- [ ] `.env` / secrets NOT in git
- [ ] `robots.txt` and `sitemap.xml` if public site
- [ ] Favicon and meta tags set
- [ ] HTTPS configured (automatic on Vercel/Railway)
- [ ] Error pages (404, 500) configured
- [ ] Performance: images optimized, code split, no huge bundles

## Rollback

```bash
# Vercel — redeploy previous
npx vercel rollback

# Railway — redeploy previous
railway rollback

# Git-based — revert and push
git revert HEAD && git push
```

## Domain Setup

```bash
# Vercel
npx vercel domains add mydomain.com

# DNS: Point CNAME to cname.vercel-dns.com
# Or A record to 76.76.21.21
```
