---
name: internet-lookup-verifier
description: Verify information by performing an internet lookup before answering questions.
---
# Internet Lookup Verifier

## Purpose
When a user asks a factual question, this skill performs an online search to confirm the answer and returns a concise verified response. It ensures that the assistant’s reply is backed by current, reliable sources.

## How it works
1. **Trigger** – The skill activates when the system prompt or another skill signals a need for verification. Typically this happens before answering a question that contains keywords like *fact*, *true/false*, *verify*, or *source*.
2. **Search** – Uses the `web_search` tool to retrieve up to 5 relevant results (default 3). The query is the user’s question or a re‑phrased version suitable for search engines.
3. **Extract** – From each result, the skill pulls the title, URL and snippet. If needed, it can fetch the full page with `web_fetch` for deeper analysis.
4. **Evaluate** – The assistant checks that at least one source explicitly supports the answer. If sources disagree or none are found, it reports uncertainty.
5. **Respond** – Returns a short verified answer followed by a list of URLs (and optionally snippets) that back the claim.

## Usage example
> *User:* Is the capital of Australia Canberra?
> 
> *Assistant (using this skill):* Yes, Canberra is the capital of Australia. Source: https://www.britannica.com/place/Canberra-Australia

## Limitations
- Relies on the quality of public search results.
- May not handle niche or very new information if it hasn’t indexed yet.
- Does not guarantee 100 % accuracy; it only indicates that sources support the claim.

## Extensibility
Add a `references/` folder with detailed guidelines for interpreting ambiguous results or handling conflicting sources. The skill can be extended to use more advanced NLP techniques for source credibility scoring.
