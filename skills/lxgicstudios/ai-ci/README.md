# ai-ci

[![npm version](https://img.shields.io/npm/v/ai-ci.svg)](https://www.npmjs.com/package/ai-ci)
[![npm downloads](https://img.shields.io/npm/dm/ai-ci.svg)](https://www.npmjs.com/package/ai-ci)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered CI/CD workflow generator. Creates GitHub Actions pipelines from project analysis.

Setting up CI/CD from scratch is a pain. This tool looks at your project and generates the right GitHub Actions workflow for it.

## Install

```bash
npm install -g ai-ci
```

## Usage

```bash
# Generate a GitHub Actions workflow
npx ai-ci

# Specify provider and deploy target
npx ai-ci --provider github --deploy vercel

# Preview without writing
npx ai-ci --preview

# Different deploy targets
npx ai-ci --deploy netlify
npx ai-ci --deploy aws
npx ai-ci --deploy docker
```

## What it does

Scans your project to figure out the language, framework, test setup, and build steps. Then generates a proper CI/CD workflow with linting, testing, building, and deployment configured.

## Supported

- **Providers**: GitHub Actions (more coming)
- **Deploy targets**: Vercel, Netlify, AWS, Docker, Fly.io, Railway
- **Languages**: Node.js, Python, Go, Rust, Ruby, Java

## Requirements

Set your `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
