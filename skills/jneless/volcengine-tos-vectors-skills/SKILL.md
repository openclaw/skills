---
name: tos-vectors
description: Manage vector storage and similarity search using TOS Vectors service. Use when working with embeddings, semantic search, RAG systems, recommendation engines, or when the user mentions vector databases, similarity search, or TOS Vectors operations.
---

# TOS Vectors Skill

Comprehensive skill for managing vector storage, indexing, and similarity search using the TOS Vectors service - a cloud-based vector database optimized for AI applications.

## Quick Start

### Initialize Client

```python
import os
import tos

# Get credentials from environment
ak = os.getenv('TOS_ACCESS_KEY')
sk = os.getenv('TOS_SECRET_KEY')
account_id = os.getenv('TOS_ACCOUNT_ID')

# Configure endpoint and region
endpoint = 'https://tosvectors-cn-beijing.volces.com'
region = 'cn-beijing'

# Create client
client = tos.VectorClient(ak, sk, endpoint, region)
```

### Basic Workflow

```python
# 1. Create vector bucket (like a database)
client.create_vector_bucket('my-vectors')

# 2. Create vector index (like a table)
client.create_index(
    account_id=account_id,
    vector_bucket_name='my-vectors',
    index_name='embeddings-768d',
    data_type=tos.DataType.DataTypeFloat32,
    dimension=768,
    distance_metric=tos.DistanceMetricType.DistanceMetricCosine
)

# 3. Insert vectors
vectors = [
    tos.models2.Vector(
        key='doc-1',
        data=tos.models2.VectorData(float32=[0.1] * 768),
        metadata={'title': 'Document 1', 'category': 'tech'}
    )
]
client.put_vectors(
    vector_bucket_name='my-vectors',
    account_id=account_id,
    index_name='embeddings-768d',
    vectors=vectors
)

# 4. Search similar vectors
query_vector = tos.models2.VectorData(float32=[0.1] * 768)
results = client.query_vectors(
    vector_bucket_name='my-vectors',
    account_id=account_id,
    index_name='embeddings-768d',
    query_vector=query_vector,
    top_k=5,
    return_distance=True,
    return_metadata=True
)
```

## Core Operations

### Vector Bucket Management

**Create Bucket**
```python
client.create_vector_bucket(bucket_name)
```

**List Buckets**
```python
result = client.list_vector_buckets(max_results=100)
for bucket in result.vector_buckets:
    print(bucket.vector_bucket_name)
```

**Delete Bucket** (must be empty)
```python
client.delete_vector_bucket(bucket_name, account_id)
```

### Vector Index Management

**Create Index**
```python
client.create_index(
    account_id=account_id,
    vector_bucket_name=bucket_name,
    index_name='my-index',
    data_type=tos.DataType.DataTypeFloat32,
    dimension=128,
    distance_metric=tos.DistanceMetricType.DistanceMetricCosine
)
```

**List Indexes**
```python
result = client.list_indexes(bucket_name, account_id)
for index in result.indexes:
    print(f"{index.index_name}: {index.dimension}d")
```

### Vector Data Operations

**Insert Vectors** (batch up to 500)
```python
vectors = []
for i in range(100):
    vector = tos.models2.Vector(
        key=f'vec-{i}',
        data=tos.models2.VectorData(float32=[...]),
        metadata={'category': 'example'}
    )
    vectors.append(vector)

client.put_vectors(
    vector_bucket_name=bucket_name,
    account_id=account_id,
    index_name=index_name,
    vectors=vectors
)
```

**Query Similar Vectors** (KNN search)
```python
results = client.query_vectors(
    vector_bucket_name=bucket_name,
    account_id=account_id,
    index_name=index_name,
    query_vector=query_vector,
    top_k=10,
    filter={"$and": [{"category": "tech"}]},  # Optional metadata filter
    return_distance=True,
    return_metadata=True
)

for vec in results.vectors:
    print(f"Key: {vec.key}, Distance: {vec.distance}")
```

**Get Vectors by Keys**
```python
result = client.get_vectors(
    vector_bucket_name=bucket_name,
    account_id=account_id,
    index_name=index_name,
    keys=['vec-1', 'vec-2'],
    return_data=True,
    return_metadata=True
)
```

**Delete Vectors**
```python
client.delete_vectors(
    vector_bucket_name=bucket_name,
    account_id=account_id,
    index_name=index_name,
    keys=['vec-1', 'vec-2']
)
```

## Common Use Cases

### 1. Semantic Search
Build a semantic search system for documents:

```python
# Index documents
for doc in documents:
    embedding = get_embedding(doc.text)  # Your embedding model
    vector = tos.models2.Vector(
        key=doc.id,
        data=tos.models2.VectorData(float32=embedding),
        metadata={'title': doc.title, 'content': doc.text[:500]}
    )
    vectors.append(vector)

client.put_vectors(
    vector_bucket_name=bucket_name,
    account_id=account_id,
    index_name=index_name,
    vectors=vectors
)

# Search
query_embedding = get_embedding(user_query)
results = client.query_vectors(
    vector_bucket_name=bucket_name,
    account_id=account_id,
    index_name=index_name,
    query_vector=tos.models2.VectorData(float32=query_embedding),
    top_k=5,
    return_metadata=True
)
```

### 2. RAG (Retrieval Augmented Generation)
Retrieve relevant context for LLM prompts:

```python
# Retrieve relevant documents
question_embedding = get_embedding(user_question)
search_results = client.query_vectors(
    vector_bucket_name=bucket_name,
    account_id=account_id,
    index_name='knowledge-base',
    query_vector=tos.models2.VectorData(float32=question_embedding),
    top_k=3,
    return_metadata=True
)

# Build context
context = "\n\n".join([
    v.metadata.get('content', '') for v in search_results.vectors
])

# Generate answer with LLM
prompt = f"Context:\n{context}\n\nQuestion: {user_question}"
```

### 3. Recommendation System
Find similar items based on user preferences:

```python
# Query with metadata filtering
results = client.query_vectors(
    vector_bucket_name=bucket_name,
    account_id=account_id,
    index_name='products',
    query_vector=user_preference_vector,
    top_k=10,
    filter={"$and": [{"category": "electronics"}, {"price_range": "mid"}]},
    return_metadata=True
)
```

## Best Practices

### Naming Conventions
- **Bucket names**: 3-32 chars, lowercase letters, numbers, hyphens only
- **Index names**: 3-63 chars
- **Vector keys**: 1-1024 chars, use meaningful identifiers

### Batch Operations
- Insert up to 500 vectors per call
- Delete up to 100 vectors per call
- Use pagination for listing operations

### Error Handling
```python
try:
    result = client.create_vector_bucket(bucket_name)
except tos.exceptions.TosClientError as e:
    print(f'Client error: {e.message}')
except tos.exceptions.TosServerError as e:
    print(f'Server error: {e.code}, Request ID: {e.request_id}')
```

### Performance Tips
- Choose appropriate vector dimensions (balance accuracy vs performance)
- Use metadata filtering to reduce search space
- Use cosine similarity for normalized vectors
- Use Euclidean distance for absolute distances

## Important Limits

- **Vector buckets**: Max 100 per account
- **Vector dimensions**: 1-4096
- **Batch insert**: 1-500 vectors per call
- **Batch get/delete**: 1-100 vectors per call
- **Query TopK**: 1-30 results

## Additional Resources

For detailed API reference, see [REFERENCE.md](REFERENCE.md)
For complete workflows, see [WORKFLOWS.md](WORKFLOWS.md)
For example scripts, see the `scripts/` directory
