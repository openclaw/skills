-- =============================================================================
-- Snowflake MCP Server SQL Examples
-- Run these in Snowsight SQL Worksheet
-- =============================================================================

-- -----------------------------------------------------------------------------
-- BASIC: SQL Execution Only
-- -----------------------------------------------------------------------------
CREATE OR REPLACE MCP SERVER basic_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries against the Snowflake database."
    title: "SQL Execution"
$$;

-- -----------------------------------------------------------------------------
-- WITH CORTEX SEARCH (RAG over unstructured data)
-- Requires: Cortex Search Service created via Snowsight UI
-- -----------------------------------------------------------------------------
CREATE OR REPLACE MCP SERVER search_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Document Search"
    identifier: "MY_DB.MY_SCHEMA.MY_SEARCH_SERVICE"
    type: "CORTEX_SEARCH_SERVICE_QUERY"
    description: "Search and retrieve information from documents and knowledge base."
    title: "Document Search"
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries."
    title: "SQL Execution"
$$;

-- -----------------------------------------------------------------------------
-- WITH CORTEX ANALYST (Natural language to SQL)
-- Requires: Semantic View or YAML file in a stage
-- -----------------------------------------------------------------------------
CREATE OR REPLACE MCP SERVER analyst_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Sales Analytics"
    identifier: "ANALYTICS_DB.MODELS.SALES_SEMANTIC_VIEW"
    type: "CORTEX_ANALYST_MESSAGE"
    description: "Query sales data, revenue metrics, and business KPIs using natural language."
    title: "Sales Analytics"
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries."
    title: "SQL Execution"
$$;

-- For YAML file in stage:
-- identifier: "@ANALYTICS_DB.MODELS.SEMANTIC_STAGE/sales_model.yaml"

-- -----------------------------------------------------------------------------
-- WITH CORTEX AGENT
-- Requires: Cortex Agent created in Snowflake
-- -----------------------------------------------------------------------------
CREATE OR REPLACE MCP SERVER agent_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Documentation Agent"
    identifier: "AGENTS_DB.PUBLIC.DOCS_AGENT"
    type: "CORTEX_AGENT_RUN"
    description: "An intelligent agent that answers questions about documentation."
    title: "Documentation Agent"
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries."
    title: "SQL Execution"
$$;

-- -----------------------------------------------------------------------------
-- WITH CUSTOM TOOL (Stored Procedure)
-- Requires: Stored procedure with proper signature
-- -----------------------------------------------------------------------------

-- First, create the stored procedure
CREATE OR REPLACE PROCEDURE MY_DB.DATA.SEND_EMAIL(
    body STRING,
    recipient_email STRING,
    subject STRING
)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'send_email'
AS
$$
def send_email(session, body, recipient_email, subject):
    # Implementation here
    return f"Email sent to {recipient_email}"
$$;

-- Then create MCP server with custom tool
CREATE OR REPLACE MCP SERVER custom_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Send_Email"
    identifier: "MY_DB.DATA.SEND_EMAIL"
    type: "GENERIC"
    description: "Send emails to verified email addresses."
    title: "Send Email"
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        properties:
          body:
            description: "Email body content. Use HTML syntax."
            type: "string"
          recipient_email:
            description: "Recipient email address."
            type: "string"
          subject:
            description: "Email subject line."
            type: "string"
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries."
    title: "SQL Execution"
$$;

-- -----------------------------------------------------------------------------
-- FULL FEATURED SERVER (All tool types)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE MCP SERVER full_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Financial Analytics"
    identifier: "ANALYTICS_DB.DATA.FINANCIAL_SEMANTIC_VIEW"
    type: "CORTEX_ANALYST_MESSAGE"
    description: "Query financial metrics, customer data, transactions, and risk assessments using natural language."
    title: "Financial Analytics"
  - name: "Support Tickets Search"
    identifier: "SUPPORT_DB.DATA.TICKETS_SEARCH"
    type: "CORTEX_SEARCH_SERVICE_QUERY"
    description: "Search support tickets, customer interactions, and knowledge base articles."
    title: "Support Search"
  - name: "Documentation Agent"
    identifier: "AGENTS_DB.PUBLIC.DOCS_AGENT"
    type: "CORTEX_AGENT_RUN"
    description: "An agent that answers questions about company documentation."
    title: "Documentation Agent"
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries against Snowflake database."
    title: "SQL Execution"
  - name: "Send_Email"
    identifier: "UTILS_DB.DATA.SEND_EMAIL"
    type: "GENERIC"
    description: "Send emails to verified addresses."
    title: "Send Email"
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        properties:
          body:
            description: "Email body in HTML format."
            type: "string"
          recipient_email:
            description: "Recipient email address."
            type: "string"
          subject:
            description: "Email subject line."
            type: "string"
$$;

-- -----------------------------------------------------------------------------
-- UTILITY QUERIES
-- -----------------------------------------------------------------------------

-- List all MCP servers in current schema
SHOW MCP SERVERS;

-- Describe an MCP server
DESCRIBE MCP SERVER my_mcp_server;

-- Drop an MCP server
DROP MCP SERVER my_mcp_server;

-- Get your account identifier (for connection URL)
SELECT CURRENT_ACCOUNT();
SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME();
