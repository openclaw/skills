---
name: eleutherios
description: Epistemic analysis infrastructure - query knowledge graphs with suppression detection, coordination signatures, and multi-perspective clustering. Local-first, no cloud dependencies.
version: 1.1.0
author: Cedrus Strategic LLC
repository: https://github.com/Eleutherios-project/Eleutherios-docker
homepage: https://eleutherios.io
license: MIT
tags:
  - research
  - knowledge-graph
  - analysis
  - mcp
  - epistemic
  - osint
  - document-analysis
metadata:
  openclaw:
    mcp:
      server: "http://localhost:8100/mcp"
      transport: "streamable-http"
    requirements:
      - "Docker and Docker Compose"
      - "Eleutherios running locally (see setup below)"
    config:
      requiredEnv: []
      stateDirs: []
---

# Eleutherios - Epistemic Analysis Infrastructure

Query knowledge graphs built from your document collections. Detect suppression patterns, coordination signatures, and get multi-perspective analysis on contested topics.

## What This Skill Does

Eleutherios transforms document collections into knowledge graphs with claim-level extraction, then runs detection algorithms to surface patterns that traditional search misses:

- **Suppression Detection**: Identifies funding cuts, career impacts, publication obstacles, and institutional marginalization patterns documented within sources
- **Coordination Signatures**: Detects timing patterns, shared language, and citation network anomalies suggesting coordinated messaging
- **Multi-Perspective Clustering**: Groups claims by viewpoint so you can see all sides of contested topics
- **Source Topology Analysis**: Maps citation networks and trust relationships between sources

## When to Use This Skill

Use Eleutherios when you need to:

- Research topics where institutional consensus may be manufactured
- Analyze historical documents for suppression patterns (e.g., declassified materials, congressional testimony)
- Compare how different sources treat the same topic
- Build understanding of contested scientific or historical debates
- Investigate citation voids and research threads that mysteriously dead-end

Example prompts:
- "What does Eleutherios show about suppression patterns for Thomas Paine?"
- "Get perspectives on plasma propulsion research from my knowledge graph"
- "Analyze the topic of electrogravitics - what sources exist and what patterns emerge?"
- "Assess the source topology for the Smedley Butler FBI files"

## Prerequisites

**Eleutherios must be running locally before using this skill.**

### Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/Eleutherios-project/Eleutherios-docker.git
cd Eleutherios-docker

# Start the stack
docker-compose up -d

# Verify MCP server is running
curl http://localhost:8100/health
```

The MCP server runs on port 8100 by default. The web UI is available at http://localhost:8080.

### Importing Documents

Use the web UI or CLI to import your document collection:

```bash
# Via CLI
docker exec -it eleutherios-api python aegis_import_wizard.py /path/to/documents

# Or use the web UI at http://localhost:8080
```

Supported formats: PDF, DOCX, TXT, MD, HTML

### Verify Connection

Once Eleutherios is running, test the MCP connection:

```bash
curl -X POST http://localhost:8100/mcp/list_domains \
  -H "Content-Type: application/json" \
  -d '{}'
```

You should see a JSON response with your corpus statistics.

## Available Tools

### analyze_topic
Run suppression and coordination detection on a topic.

```
Parameters:
  - topic (required): The topic to analyze
  - detail: "brief" | "standard" | "verbose" (default: "standard")
  - max_claims: Maximum claims to analyze (default: 100)

Returns:
  - Suppression score (0.0-1.0) with severity rating
  - Coordination score with pattern indicators
  - Relevant claims with source attribution
  - Detection signals (funding impacts, credential attacks, etc.)
```

### get_perspectives
Cluster claims by viewpoint using semantic analysis.

```
Parameters:
  - topic (required): The topic to analyze
  - max_clusters: Number of perspective clusters (default: 5)
  - claims_per_cluster: Claims per cluster (default: 5)

Returns:
  - Clustered perspectives with representative claims
  - Cluster labels and themes
  - Cross-cluster relationships
```

### assess_source
Analyze a specific source's position in the knowledge topology.

```
Parameters:
  - source_identifier (required): Document title or source file name
  - detail: "brief" | "standard" | "verbose" (default: "standard")

Returns:
  - Citation network position
  - Claim types (PRIMARY vs META)
  - Trust score aggregation
  - Related sources
```

### get_claim_context
Deep dive on a specific claim with full context.

```
Parameters:
  - claim_id (required): The claim identifier
  - include_graph: Include graph relationships (default: true)

Returns:
  - Full claim text and metadata
  - Source document context
  - Related entities
  - Citation relationships
```

### list_domains
Get corpus statistics and available domains.

```
Parameters: none

Returns:
  - Total claims, documents, entities
  - Domain breakdown
  - Corpus health metrics
```

## Example Workflow

```
You: "What suppression patterns exist for Thomas Paine in my knowledge graph?"

[Skill calls analyze_topic with topic="Thomas Paine"]

Response: "Thomas Paine shows a CRITICAL suppression score of 0.831. 
Key indicators:
- Credential inversion: Despite being a Founding Father, systematically 
  marginalized in educational curricula
- Evidence avoidance: Critics attack character rather than engage arguments
- Career/social impacts: Documented ostracism, denied burial in consecrated ground

47 claims analyzed across 3 documents. Strongest signals from 
'Age of Reason' and 'Rights of Man' analysis."

You: "Show me the different perspectives on his work"

[Skill calls get_perspectives with topic="Thomas Paine"]

Response: "Found 4 distinct perspective clusters:
1. Revolutionary Hero (12 claims) - Focus on Common Sense, independence
2. Religious Critic (9 claims) - Age of Reason, deism arguments  
3. Institutional Dismissal (8 claims) - Character attacks, marginalization
4. Modern Rehabilitation (6 claims) - Academic reassessment

Cluster 3 shows classic suppression rhetoric: ad hominem attacks
without substantive engagement with Cluster 2's actual arguments."
```

## Configuration

### Custom MCP Port

If running Eleutherios on a different port, update your OpenClaw config:

```yaml
# In your OpenClaw workspace skills config
eleutherios:
  mcp:
    server: "http://localhost:YOUR_PORT/mcp"
```

### Remote Server

For remote Eleutherios instances (e.g., on a homelab server):

```yaml
eleutherios:
  mcp:
    server: "http://192.168.1.100:8100/mcp"
```

**Security Note**: Only expose Eleutherios on trusted networks. The MCP server has no authentication by default.

## Troubleshooting

### "Connection refused" errors
- Verify Eleutherios is running: `docker ps | grep eleutherios`
- Check the MCP port: `curl http://localhost:8100/health`
- Ensure no firewall blocking port 8100

### Empty results
- Verify documents have been imported: check web UI at localhost:8080
- Run extraction if needed: documents must be processed before querying

### Slow responses
- Large corpus queries may take 10-30 seconds
- Use `max_claims` parameter to limit scope
- Consider running on hardware with GPU for faster embedding generation

## Privacy & Security

- **Local-first**: All data stays on your machine. No cloud dependencies.
- **No telemetry**: Eleutherios sends no data externally.
- **Your documents, your analysis**: Build knowledge graphs from your own curated collections.

## Links

- **Website**: https://eleutherios.io
- **GitHub**: https://github.com/Eleutherios-project/
- **Documentation**: https://github.com/Eleutherios-project/Eleutherios-docker/blob/main/README.md
- **Issues**: https://github.com/Eleutherios-project/Eleutherios-docker/issues

## About

Eleutherios (from Zeus Eleutherios, god of freedom) is open-source epistemic defense infrastructure. Built for researchers investigating topics where institutional gatekeepers cannot be trusted.

Created by Cedrus Strategic LLC. MIT Licensed.
