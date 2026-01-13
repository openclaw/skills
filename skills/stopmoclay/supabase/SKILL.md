---
name: supabase
description: Connect to Supabase for database operations, vector search, and storage. Use for storing data, running SQL queries, similarity search with pgvector, and managing tables. Triggers on requests involving databases, vector stores, embeddings, or Supabase specifically.
metadata: {"clawdbot":{"requires":{"env":["SUPABASE_URL","SUPABASE_SERVICE_KEY"]}}}
---

# Supabase CLI

Interact with Supabase projects: queries, CRUD, vector search, and table management.

## Setup

```bash
# Required
export SUPABASE_URL="https://yourproject.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIs..."

# Optional: for management API
export SUPABASE_ACCESS_TOKEN="sbp_xxxxx"
```

## Quick Commands

```bash
# SQL query
{baseDir}/scripts/supabase.sh query "SELECT * FROM users LIMIT 5"

# Insert data
{baseDir}/scripts/supabase.sh insert users '{"name": "John", "email": "john@example.com"}'

# Select with filters
{baseDir}/scripts/supabase.sh select users --eq "status:active" --limit 10

# Update
{baseDir}/scripts/supabase.sh update users '{"status": "inactive"}' --eq "id:123"

# Delete
{baseDir}/scripts/supabase.sh delete users --eq "id:123"

# Vector similarity search
{baseDir}/scripts/supabase.sh vector-search documents "search query" --match-fn match_documents --limit 5

# List tables
{baseDir}/scripts/supabase.sh tables

# Describe table
{baseDir}/scripts/supabase.sh describe users
```

## Commands Reference

### query - Run raw SQL

```bash
{baseDir}/scripts/supabase.sh query "<SQL>"

# Examples
{baseDir}/scripts/supabase.sh query "SELECT COUNT(*) FROM users"
{baseDir}/scripts/supabase.sh query "CREATE TABLE items (id serial primary key, name text)"
{baseDir}/scripts/supabase.sh query "SELECT * FROM users WHERE created_at > '2024-01-01'"
```

### select - Query table with filters

```bash
{baseDir}/scripts/supabase.sh select <table> [options]

Options:
  --columns <cols>    Comma-separated columns (default: *)
  --eq <col:val>      Equal filter (can use multiple)
  --neq <col:val>     Not equal filter
  --gt <col:val>      Greater than
  --lt <col:val>      Less than
  --like <col:val>    Pattern match (use % for wildcard)
  --limit <n>         Limit results
  --offset <n>        Offset results
  --order <col>       Order by column
  --desc              Descending order

# Examples
{baseDir}/scripts/supabase.sh select users --eq "status:active" --limit 10
{baseDir}/scripts/supabase.sh select posts --columns "id,title,created_at" --order created_at --desc
{baseDir}/scripts/supabase.sh select products --gt "price:100" --lt "price:500"
```

### insert - Insert row(s)

```bash
{baseDir}/scripts/supabase.sh insert <table> '<json>'

# Single row
{baseDir}/scripts/supabase.sh insert users '{"name": "Alice", "email": "alice@test.com"}'

# Multiple rows
{baseDir}/scripts/supabase.sh insert users '[{"name": "Bob"}, {"name": "Carol"}]'
```

### update - Update rows

```bash
{baseDir}/scripts/supabase.sh update <table> '<json>' --eq <col:val>

# Example
{baseDir}/scripts/supabase.sh update users '{"status": "inactive"}' --eq "id:123"
{baseDir}/scripts/supabase.sh update posts '{"published": true}' --eq "author_id:5"
```

### upsert - Insert or update

```bash
{baseDir}/scripts/supabase.sh upsert <table> '<json>'

# Example (requires unique constraint)
{baseDir}/scripts/supabase.sh upsert users '{"id": 1, "name": "Updated Name"}'
```

### delete - Delete rows

```bash
{baseDir}/scripts/supabase.sh delete <table> --eq <col:val>

# Example
{baseDir}/scripts/supabase.sh delete sessions --lt "expires_at:2024-01-01"
```

### vector-search - Similarity search with pgvector

```bash
{baseDir}/scripts/supabase.sh vector-search <table> "<query>" [options]

Options:
  --match-fn <name>     RPC function name (default: match_<table>)
  --limit <n>           Number of results (default: 5)
  --threshold <n>       Similarity threshold 0-1 (default: 0.5)
  --embedding-model <m> Model for query embedding (default: uses OpenAI)

# Example
{baseDir}/scripts/supabase.sh vector-search documents "How to set up authentication" --limit 10

# Requires a match function like:
# CREATE FUNCTION match_documents(query_embedding vector(1536), match_threshold float, match_count int)
```

### tables - List all tables

```bash
{baseDir}/scripts/supabase.sh tables
```

### describe - Show table schema

```bash
{baseDir}/scripts/supabase.sh describe <table>
```

### rpc - Call stored procedure

```bash
{baseDir}/scripts/supabase.sh rpc <function_name> '<json_params>'

# Example
{baseDir}/scripts/supabase.sh rpc get_user_stats '{"user_id": 123}'
```

## Vector Search Setup

### 1. Enable pgvector extension

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Create table with embedding column

```sql
CREATE TABLE documents (
  id bigserial PRIMARY KEY,
  content text,
  metadata jsonb,
  embedding vector(1536)
);
```

### 3. Create similarity search function

```sql
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

### 4. Create index for performance

```sql
CREATE INDEX ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| SUPABASE_URL | Yes | Project URL (https://xxx.supabase.co) |
| SUPABASE_SERVICE_KEY | Yes | Service role key (full access) |
| SUPABASE_ANON_KEY | No | Anon key (restricted access) |
| SUPABASE_ACCESS_TOKEN | No | Management API token |
| OPENAI_API_KEY | No | For generating embeddings |

## Notes

- Service role key bypasses RLS (Row Level Security)
- Use anon key for client-side/restricted access
- Vector search requires pgvector extension
- Embeddings default to OpenAI text-embedding-ada-002 (1536 dimensions)
