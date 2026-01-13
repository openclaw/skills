#!/usr/bin/env bash
# Supabase CLI - Database operations, vector search, and more
set -euo pipefail

# Check required env vars
if [[ -z "${SUPABASE_URL:-}" ]]; then
    echo "Error: SUPABASE_URL not set" >&2
    exit 1
fi

if [[ -z "${SUPABASE_SERVICE_KEY:-}" ]]; then
    echo "Error: SUPABASE_SERVICE_KEY not set" >&2
    exit 1
fi

REST_URL="${SUPABASE_URL}/rest/v1"
RPC_URL="${SUPABASE_URL}/rest/v1/rpc"

usage() {
    cat << 'EOF'
Usage: supabase.sh <command> [args] [options]

Commands:
  query <sql>                    Run raw SQL query
  select <table>                 Select from table with filters
  insert <table> <json>          Insert row(s)
  update <table> <json>          Update rows (requires --eq filter)
  upsert <table> <json>          Insert or update
  delete <table>                 Delete rows (requires --eq filter)
  vector-search <table> <query>  Similarity search with pgvector
  tables                         List all tables
  describe <table>               Show table schema
  rpc <function> <json>          Call RPC function
  help                           Show this help

Select/Update/Delete Options:
  --columns <cols>    Columns to select (comma-separated)
  --eq <col:val>      Equal filter
  --neq <col:val>     Not equal filter
  --gt <col:val>      Greater than
  --lt <col:val>      Less than
  --gte <col:val>     Greater than or equal
  --lte <col:val>     Less than or equal
  --like <col:val>    Pattern match
  --ilike <col:val>   Case-insensitive pattern match
  --is <col:val>      IS (for null, true, false)
  --in <col:vals>     IN (comma-separated values)
  --limit <n>         Limit results
  --offset <n>        Offset results
  --order <col>       Order by column
  --desc              Descending order

Vector Search Options:
  --match-fn <name>   RPC function name (default: match_<table>)
  --limit <n>         Number of results (default: 5)
  --threshold <n>     Similarity threshold (default: 0.5)

Examples:
  supabase.sh query "SELECT * FROM users LIMIT 5"
  supabase.sh select users --eq "status:active" --limit 10
  supabase.sh insert users '{"name": "John", "email": "john@test.com"}'
  supabase.sh vector-search docs "authentication guide" --limit 5
EOF
}

# Make API request
api_request() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    local extra_headers=("${@:4}")
    
    local args=(
        -s
        -X "$method"
        -H "apikey: ${SUPABASE_SERVICE_KEY}"
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}"
        -H "Content-Type: application/json"
        -H "Prefer: return=representation"
    )
    
    for header in "${extra_headers[@]:-}"; do
        [[ -n "$header" ]] && args+=(-H "$header")
    done
    
    if [[ -n "$data" ]]; then
        args+=(-d "$data")
    fi
    
    curl "${args[@]}" "$endpoint"
}

# Run raw SQL
cmd_query() {
    local sql="${1:-}"
    if [[ -z "$sql" ]]; then
        echo "Error: SQL query required" >&2
        exit 1
    fi
    
    local response
    response=$(api_request POST "${RPC_URL}/exec_sql" "{\"query\": $(printf '%s' "$sql" | jq -Rs .)}" 2>/dev/null || true)
    
    # If exec_sql doesn't exist, try the query endpoint
    if [[ "$response" == *"Could not find"* ]] || [[ -z "$response" ]]; then
        # Fall back to direct query via PostgREST (limited)
        echo "Note: Direct SQL requires exec_sql function. Using REST API..." >&2
        echo "Create function: CREATE FUNCTION exec_sql(query text) RETURNS json AS \$\$ ... \$\$" >&2
        exit 1
    fi
    
    echo "$response" | jq .
}

# Build filter query string
build_filters() {
    local filters=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --eq)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=eq.${val}"
                shift 2
                ;;
            --neq)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=neq.${val}"
                shift 2
                ;;
            --gt)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=gt.${val}"
                shift 2
                ;;
            --lt)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=lt.${val}"
                shift 2
                ;;
            --gte)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=gte.${val}"
                shift 2
                ;;
            --lte)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=lte.${val}"
                shift 2
                ;;
            --like)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=like.${val}"
                shift 2
                ;;
            --ilike)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=ilike.${val}"
                shift 2
                ;;
            --is)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=is.${val}"
                shift 2
                ;;
            --in)
                local col="${2%%:*}"
                local val="${2#*:}"
                filters+="&${col}=in.(${val})"
                shift 2
                ;;
            --limit)
                filters+="&limit=${2}"
                shift 2
                ;;
            --offset)
                filters+="&offset=${2}"
                shift 2
                ;;
            --order)
                ORDER_COL="$2"
                shift 2
                ;;
            --desc)
                ORDER_DESC=true
                shift
                ;;
            --columns)
                SELECT_COLS="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Add ordering
    if [[ -n "${ORDER_COL:-}" ]]; then
        if [[ "${ORDER_DESC:-false}" == true ]]; then
            filters+="&order=${ORDER_COL}.desc"
        else
            filters+="&order=${ORDER_COL}"
        fi
    fi
    
    echo "$filters"
}

# Select from table
cmd_select() {
    local table="${1:-}"
    shift || true
    
    if [[ -z "$table" ]]; then
        echo "Error: Table name required" >&2
        exit 1
    fi
    
    ORDER_COL=""
    ORDER_DESC=false
    SELECT_COLS="*"
    
    local filters
    filters=$(build_filters "$@")
    
    local url="${REST_URL}/${table}?select=${SELECT_COLS}${filters}"
    api_request GET "$url" | jq .
}

# Insert into table
cmd_insert() {
    local table="${1:-}"
    local data="${2:-}"
    
    if [[ -z "$table" ]] || [[ -z "$data" ]]; then
        echo "Error: Table and JSON data required" >&2
        echo "Usage: supabase.sh insert <table> '<json>'" >&2
        exit 1
    fi
    
    api_request POST "${REST_URL}/${table}" "$data" | jq .
}

# Update table
cmd_update() {
    local table="${1:-}"
    local data="${2:-}"
    shift 2 || true
    
    if [[ -z "$table" ]] || [[ -z "$data" ]]; then
        echo "Error: Table and JSON data required" >&2
        exit 1
    fi
    
    ORDER_COL=""
    ORDER_DESC=false
    SELECT_COLS=""
    
    local filters
    filters=$(build_filters "$@")
    
    if [[ -z "$filters" ]]; then
        echo "Error: At least one filter required for update (use --eq)" >&2
        exit 1
    fi
    
    local url="${REST_URL}/${table}?${filters:1}"
    api_request PATCH "$url" "$data" | jq .
}

# Upsert into table
cmd_upsert() {
    local table="${1:-}"
    local data="${2:-}"
    
    if [[ -z "$table" ]] || [[ -z "$data" ]]; then
        echo "Error: Table and JSON data required" >&2
        exit 1
    fi
    
    api_request POST "${REST_URL}/${table}" "$data" "Prefer: resolution=merge-duplicates" | jq .
}

# Delete from table
cmd_delete() {
    local table="${1:-}"
    shift || true
    
    if [[ -z "$table" ]]; then
        echo "Error: Table name required" >&2
        exit 1
    fi
    
    ORDER_COL=""
    ORDER_DESC=false
    SELECT_COLS=""
    
    local filters
    filters=$(build_filters "$@")
    
    if [[ -z "$filters" ]]; then
        echo "Error: At least one filter required for delete (use --eq)" >&2
        exit 1
    fi
    
    local url="${REST_URL}/${table}?${filters:1}"
    api_request DELETE "$url" | jq .
}

# Vector similarity search
cmd_vector_search() {
    local table="${1:-}"
    local query="${2:-}"
    shift 2 || true
    
    if [[ -z "$table" ]] || [[ -z "$query" ]]; then
        echo "Error: Table and query required" >&2
        echo "Usage: supabase.sh vector-search <table> \"<query>\" [options]" >&2
        exit 1
    fi
    
    local match_fn="match_${table}"
    local limit=5
    local threshold=0.5
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --match-fn)
                match_fn="$2"
                shift 2
                ;;
            --limit)
                limit="$2"
                shift 2
                ;;
            --threshold)
                threshold="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Generate embedding using OpenAI
    if [[ -z "${OPENAI_API_KEY:-}" ]]; then
        echo "Error: OPENAI_API_KEY required for vector search" >&2
        exit 1
    fi
    
    local embedding
    embedding=$(curl -s https://api.openai.com/v1/embeddings \
        -H "Authorization: Bearer ${OPENAI_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"input\": $(printf '%s' "$query" | jq -Rs .), \"model\": \"text-embedding-ada-002\"}" \
        | jq -c '.data[0].embedding')
    
    if [[ "$embedding" == "null" ]] || [[ -z "$embedding" ]]; then
        echo "Error: Failed to generate embedding" >&2
        exit 1
    fi
    
    # Call RPC function
    local params
    params=$(jq -n \
        --argjson embedding "$embedding" \
        --argjson threshold "$threshold" \
        --argjson limit "$limit" \
        '{query_embedding: $embedding, match_threshold: $threshold, match_count: $limit}')
    
    api_request POST "${RPC_URL}/${match_fn}" "$params" | jq .
}

# List tables
cmd_tables() {
    # Query information_schema
    local response
    response=$(api_request GET "${REST_URL}/information_schema.tables?select=table_name&table_schema=eq.public" 2>/dev/null || true)
    
    if [[ -z "$response" ]] || [[ "$response" == *"permission denied"* ]]; then
        echo "Tables (from REST API):"
        # Try to list from REST endpoint directly
        curl -s -I -X GET "${REST_URL}/" \
            -H "apikey: ${SUPABASE_SERVICE_KEY}" \
            -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" 2>/dev/null \
            | grep -i "x-" | head -20
    else
        echo "$response" | jq -r '.[].table_name' 2>/dev/null || echo "$response"
    fi
}

# Describe table
cmd_describe() {
    local table="${1:-}"
    
    if [[ -z "$table" ]]; then
        echo "Error: Table name required" >&2
        exit 1
    fi
    
    # Get column info via HEAD request
    echo "Table: $table"
    echo "Columns:"
    curl -s -I -X GET "${REST_URL}/${table}?limit=0" \
        -H "apikey: ${SUPABASE_SERVICE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" 2>/dev/null \
        | grep -i "content-profile\|x-" | head -10
    
    # Try to get a sample row
    echo ""
    echo "Sample (1 row):"
    api_request GET "${REST_URL}/${table}?limit=1" | jq .
}

# Call RPC function
cmd_rpc() {
    local fn="${1:-}"
    local params="${2:-"{}"}"
    
    if [[ -z "$fn" ]]; then
        echo "Error: Function name required" >&2
        exit 1
    fi
    
    api_request POST "${RPC_URL}/${fn}" "$params" | jq .
}

# Main
case "${1:-help}" in
    query)
        shift
        cmd_query "$@"
        ;;
    select)
        shift
        cmd_select "$@"
        ;;
    insert)
        shift
        cmd_insert "$@"
        ;;
    update)
        shift
        cmd_update "$@"
        ;;
    upsert)
        shift
        cmd_upsert "$@"
        ;;
    delete)
        shift
        cmd_delete "$@"
        ;;
    vector-search|vs)
        shift
        cmd_vector_search "$@"
        ;;
    tables)
        cmd_tables
        ;;
    describe)
        shift
        cmd_describe "$@"
        ;;
    rpc)
        shift
        cmd_rpc "$@"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo "Unknown command: $1" >&2
        usage
        exit 1
        ;;
esac
