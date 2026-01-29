/**
 * WeCom MCP Server
 * 
 * Send messages to WeCom (企业微信) via incoming webhooks
 * 
 * Usage:
 *   npm install
 *   npm run build
 *   export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
 *   node dist/index.js
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import axios from "axios";

const WECOM_WEBHOOK_URL = process.env.WECOM_WEBHOOK_URL;
const WECOM_TIMEOUT_MS = parseInt(process.env.WECOM_TIMEOUT_MS || "10000", 10);

if (!WECOM_WEBHOOK_URL) {
  console.error("Error: WECOM_WEBHOOK_URL environment variable is required");
  process.exit(1);
}

const server = new Server({
  name: "wecom-bot-mcp-server",
  version: "1.0.0",
});

// Register server capabilities
server.registerCapabilities({
  tools: {},
});

// Tool: send_wecom_message
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "send_wecom_message") {
    const content = args?.content as string;
    const mentioned_list = args?.mentioned_list as string[] | undefined;

    if (!content) {
      throw new Error("content is required");
    }

    try {
      const response = await axios.post(
        WECOM_WEBHOOK_URL,
        {
          msgtype: "text",
          text: {
            content,
            mentioned_list: mentioned_list || [],
          },
        },
        {
          timeout: WECOM_TIMEOUT_MS,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data?.errcode !== 0 && response.data?.errcode !== undefined) {
        throw new Error(`WeCom API error: ${response.data.errmsg}`);
      }

      return {
        content: [
          {
            type: "text",
            text: "Message sent to WeCom successfully",
          },
        ],
      };
    } catch (error: any) {
      throw new Error(`Failed to send WeCom message: ${error.message}`);
    }
  }

  if (name === "send_wecom_markdown") {
    const content = args?.content as string;

    if (!content) {
      throw new Error("content is required");
    }

    try {
      const response = await axios.post(
        WECOM_WEBHOOK_URL,
        {
          msgtype: "markdown",
          markdown: {
            content,
          },
        },
        {
          timeout: WECOM_TIMEOUT_MS,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data?.errcode !== 0 && response.data?.errcode !== undefined) {
        throw new Error(`WeCom API error: ${response.data.errmsg}`);
      }

      return {
        content: [
          {
            type: "text",
            text: "Markdown message sent to WeCom successfully",
          },
        ],
      };
    } catch (error: any) {
      throw new Error(`Failed to send WeCom markdown: ${error.message}`);
    }
  }

  throw new Error(`Unknown tool: ${name}`);
});

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "send_wecom_message",
        description: "Send a text message to WeCom via webhook",
        inputSchema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "Message content to send",
            },
            mentioned_list: {
              type: "array",
              description: "List of userids to mention (WeCom userids)",
              items: {
                type: "string",
              },
            },
          },
          required: ["content"],
        },
      },
      {
        name: "send_wecom_markdown",
        description: "Send a markdown message to WeCom via webhook",
        inputSchema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "Markdown content to send",
            },
          },
          required: ["content"],
        },
      },
    ],
  };
});

// Start server
const transport = new StdioServerTransport();
server.connect(transport);

console.error("WeCom MCP Server running on stdio");
