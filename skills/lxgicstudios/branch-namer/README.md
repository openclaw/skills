# ai-branch

Stop wasting time thinking up branch names. Just describe what you're doing and get a clean, conventional branch name back.

## Install

```bash
npm install -g ai-branch
```

## Usage

```bash
npx ai-branch "Add dark mode to settings"
# → feat/add-dark-mode-settings

npx ai-branch "Fix login redirect loop" --checkout
# → fix/login-redirect-loop (and checks it out)
```

## Setup

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=sk-...
```

That's it. It'll pick the right prefix (feat, fix, chore, etc.) and format everything in kebab-case.

## Options

- `-c, --checkout` - Create the branch and switch to it automatically

## How it works

Sends your description to GPT-4o-mini, gets back a properly formatted branch name. Uses conventional prefixes so your git history stays clean.

## License

MIT
