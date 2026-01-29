# TOS Vectors Agent Skill

A comprehensive Claude Agent Skill for managing vector storage and similarity search using TOS Vectors service.

## Overview

This skill enables Claude to work with TOS Vectors - a cloud-based vector database optimized for AI applications including semantic search, RAG systems, and recommendation engines.

## Skill Structure

```
tos-vectors-skill/
├── SKILL.md              # Main skill file with quick start and core operations
├── REFERENCE.md          # Complete API reference
├── WORKFLOWS.md          # Common workflow patterns
├── scripts/              # Utility scripts
│   ├── init_vectors.py   # Initialize bucket and index
│   ├── insert_vectors.py # Insert sample vectors
│   └── search_vectors.py # Search vectors
└── examples/             # Additional examples
```

## Quick Start

### 1. Set Environment Variables

```bash
export TOS_ACCESS_KEY="your-access-key"
export TOS_SECRET_KEY="your-secret-key"
export TOS_ACCOUNT_ID="your-account-id"
```

### 2. Initialize Environment

```bash
python scripts/init_vectors.py
```

### 3. Insert Sample Data

```bash
python scripts/insert_vectors.py
```

### 4. Search Vectors

```bash
python scripts/search_vectors.py "machine learning"
```

## Core Capabilities

- **Vector Bucket Management**: Create, list, delete vector buckets
- **Vector Index Management**: Create indexes with custom dimensions and metrics
- **Vector Operations**: Insert, query, get, delete, and list vectors
- **Similarity Search**: KNN search with metadata filtering
- **Batch Operations**: Efficient batch insert/delete (up to 500/100 vectors)
- **Policy Management**: IAM policy configuration

## Common Use Cases

1. **Semantic Search**: Build document search systems
2. **RAG Systems**: Retrieval augmented generation for LLMs
3. **Recommendations**: Product/content recommendation engines
4. **Image Search**: Visual similarity search

## Documentation

- **SKILL.md**: Quick reference and common operations
- **REFERENCE.md**: Complete API documentation
- **WORKFLOWS.md**: Step-by-step workflow examples

## Requirements

- Python 3.7+
- `tos` Python SDK
- TOS Vectors account credentials

## Installation

```bash
pip install tos
```

## Configuration

### Endpoints

- **Internal**: `https://tosvectors-cn-beijing.ivolces.com`
- **External**: `https://tosvectors-cn-beijing.volces.com`

### Regions

- `cn-beijing` (Beijing)
- `cn-shanghai` (Shanghai)
- `cn-guangzhou` (Guangzhou)

## Limits

- Max vector buckets: 100 per account
- Vector dimensions: 1-4096
- Batch insert: 1-500 vectors
- Batch get/delete: 1-100 vectors
- Query TopK: 1-30 results

## Support

For issues or questions, refer to the TOS Vectors documentation or contact support.
