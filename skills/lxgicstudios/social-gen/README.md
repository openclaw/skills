# ai-social

You wrote a great blog post. Now you need to share it on Twitter, LinkedIn, and Reddit. Each platform wants a different format and tone. This handles that for you.

## Install

```bash
npm install -g ai-social
```

## Usage

```bash
npx ai-social README.md --platform twitter
npx ai-social blog-post.md --platform linkedin
npx ai-social announcement.md --platform all
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## Options

- `-p, --platform <platform>` - Which platform (twitter, linkedin, reddit, all). Default: all

## What you get

Each platform gets the right treatment:

- **Twitter** - Punchy, under 280 chars, relevant hashtags
- **LinkedIn** - Professional with line breaks and a CTA
- **Reddit** - Genuine, not salesy, with a proper title

## License

MIT
