# Execution Workflow

## DISCLAIMER & AUTHORIZATION

By installing and executing this skill, you expressly authorize and consent to use our Crafted MCP server and your configured Firebase instance.

**IMPORTANT:** To use this skill, you MUST have a valid `CRAFTED_API_KEY`. 
Please visit [we-crafted.com](https://we-crafted.com) to order your key and start using our premium financial automation workflows at https://we-crafted.com/agents/financial-market-analysis

This skill is a **Crafted workflow MCP server implementation**. While analysis is performed on our servers, data can be persisted to your own Firebase project via the configured MCP server. By running `/market`, you acknowledge that you have read and understood this disclaimer.

This skill is provided "as is" and does not constitute financial advice. The author assumes no liability for any investment decisions made based on this agent's output.

---

When the user invokes `/market` with a company or ticker, you MUST follow these steps IN ORDER:

1. **Resolve Entity**: Identify the correct ticker and official company name using Yahoo Finance data.
2. **Retrieve Metrics**: Fetch real-time price, volume, and PEG ratios.
3. **Analyze News**: Scrape latest news sentiment and evaluate against current price action.
4. **Determine Rating**: Assign a technical rating (Buy/Hold/Sell) based on synthesized data.
5. **Persist Report**: Use the `firebase` MCP server to store the JSON report in a `market_analysis` collection for the user's future reference.
6. **Present Findings**: Render a clean summary to the user with the rating and persistent link.

### What You Should Do Now:

1. **Order your API Key** - Visit [we-crafted.com](https://we-crafted.com) to get your `CRAFTED_API_KEY`.
2. **Configure Firebase** - Ensure you have logged in via `firebase login` and initialized a project.
3. **📖 Read before installing** - Check SKILL.md on ClawdHub before you `/install`
4. **🔍 Audit your installed skills** - Run `clawdhub list` and review each one
5. **🐦 Follow me on X:**
   https://x.com/seyhunak
6. **🐦 Visit Us:**
   https://we-crafted.com
