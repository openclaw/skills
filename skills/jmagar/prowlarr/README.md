# Prowlarr Skill

Search across all your indexers and manage Prowlarr from Clawdbot.

## What It Does

- **Search releases** across all indexers (torrents + usenet)
- **Filter by type** (torrents-only, usenet-only) or category (Movies, TV, etc.)
- **TV/Movie search** by TVDB, IMDB, or TMDB ID
- **Manage indexers** — enable, disable, test, view stats
- **Sync to apps** — push indexer changes to Sonarr/Radarr

## Setup

### 1. Get Your API Key

1. Open Prowlarr web UI
2. Go to **Settings → General → Security**
3. Copy your **API Key**

### 2. Create Credentials File

```bash
mkdir -p ~/.clawdbot/credentials/prowlarr
cat > ~/.clawdbot/credentials/prowlarr/config.json << 'EOF'
{
  "url": "https://prowlarr.example.com",
  "apiKey": "your-api-key-here"
}
EOF
```

Replace:
- `https://prowlarr.example.com` with your Prowlarr URL
- `your-api-key-here` with your actual API key

### 3. Test It

```bash
./skills/prowlarr/scripts/prowlarr-api.sh status
```

## Usage Examples

### Search for releases

```bash
# Basic search
prowlarr-api.sh search "ubuntu 24.04"

# Torrents only
prowlarr-api.sh search "inception" --torrents

# Usenet only  
prowlarr-api.sh search "inception" --usenet

# Movies category (2000)
prowlarr-api.sh search "inception" --category 2000
```

### TV/Movie search by ID

```bash
# Search by TVDB ID
prowlarr-api.sh tv-search --tvdb 71663 --season 1 --episode 1

# Search by IMDB ID
prowlarr-api.sh movie-search --imdb tt0111161
```

### Indexer management

```bash
# List all indexers
prowlarr-api.sh indexers

# Check indexer stats
prowlarr-api.sh stats

# Test all indexers
prowlarr-api.sh test-all

# Sync to Sonarr/Radarr
prowlarr-api.sh sync
```

## Categories

| ID | Category |
|----|----------|
| 2000 | Movies |
| 5000 | TV |
| 3000 | Audio |
| 7000 | Books |
| 1000 | Console |
| 4000 | PC |

## Environment Variables (Alternative)

Instead of a config file, you can set:

```bash
export PROWLARR_URL="https://prowlarr.example.com"
export PROWLARR_API_KEY="your-api-key"
```

## Troubleshooting

**"Missing URL or API key"**  
→ Check your config file exists at `~/.clawdbot/credentials/prowlarr/config.json`

**Connection refused**  
→ Verify your Prowlarr URL is correct and accessible

**401 Unauthorized**  
→ Your API key is invalid — regenerate it in Prowlarr settings

## License

MIT
