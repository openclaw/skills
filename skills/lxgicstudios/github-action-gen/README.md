# ai-github-action

Generate GitHub Actions workflows from plain English. Stop copy-pasting from StackOverflow.

## Install

```bash
npm install -g ai-github-action
```

## Usage

```bash
npx ai-github-action "test and deploy on push to main"
npx ai-github-action "run eslint and prettier on PRs" --install
npx ai-github-action "build docker image and push to ECR" -o deploy.yml
```

## Options

- `--install` - Write directly to `.github/workflows/`
- `-o, --output <file>` - Write to specific file

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
