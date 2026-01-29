# ai-changelog

[![npm version](https://img.shields.io/npm/v/@lxgicstudios/ai-changelog.svg)](https://www.npmjs.com/package/@lxgicstudios/ai-changelog)
[![npm downloads](https://img.shields.io/npm/dm/@lxgicstudios/ai-changelog.svg)](https://www.npmjs.com/package/@lxgicstudios/ai-changelog)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered changelog generator from git history. Creates clean, categorized release notes.

Generates a clean, categorized changelog from your git history. You give it two refs (tags, branches, commits) and it reads the log between them, then uses OpenAI to turn that mess of commit messages into a proper CHANGELOG entry.

## Install

```bash
npm install -g ai-changelog
```

## Setup

You'll need an OpenAI API key:

```bash
export OPENAI_API_KEY=sk-your-key-here
```

## Usage

```bash
# Between two tags
npx ai-changelog --from v1.0.0 --to v2.0.0

# From a tag to HEAD
npx ai-changelog --from v1.0.0 --to HEAD

# Write directly to a file
npx ai-changelog --from v1.0.0 --to v2.0.0 -o CHANGELOG.md
```

It'll group your commits into Added, Changed, Fixed, Removed. No more hand-writing changelogs.

## What it does

1. Reads git log between the two refs you give it
2. Sends the commit list to OpenAI
3. Gets back a nicely formatted changelog entry
4. Prints it or writes it to a file

That's it. Nothing fancy, just saves you 20 minutes every release.
