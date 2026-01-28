---
name: Docker Pro Diagnostic
description: Advanced log analysis for Docker containers using signal extraction.
bins: ["python3", "docker"]
---

# Docker Pro Diagnostic

When a user asks "Why is my container failing?" or "Analyze the logs for [container]", follow these steps:

1.  **Run Extraction:** Call `python3 {{skillDir}}/log_processor.py <container_name>`.
2.  **Analyze:** Feed the output (which contains errors and context) into your reasoning engine.
3.  **Report:** Summarize the root cause. If it looks like a code error, suggest a fix. If it looks like a resource error (OOM), suggest increasing Docker memory limits.

## Example Command
`python3 log_processor.py api_gateway_prod`