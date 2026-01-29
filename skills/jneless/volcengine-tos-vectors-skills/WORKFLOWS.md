# TOS Vectors Workflows

Complete workflows for common TOS Vectors use cases.

## Table of Contents

- [Setup and Initialization](#setup-and-initialization)
- [Semantic Search System](#semantic-search-system)
- [RAG (Retrieval Augmented Generation)](#rag-retrieval-augmented-generation)
- [Recommendation System](#recommendation-system)
- [Vector Data Maintenance](#vector-data-maintenance)

---

## Setup and Initialization

### Complete Setup Workflow

```python
import os
import tos

# 1. Initialize client
ak = os.getenv('TOS_ACCESS_KEY')
sk = os.getenv('TOS_SECRET_KEY')
account_id = os.getenv('TOS_ACCOUNT_ID')
endpoint = 'https://tosvectors-cn-beijing.volces.com'
region = 'cn-beijing'

client = tos.VectorClient(ak, sk, endpoint, region)

# 2. Create vector bucket
bucket_name = 'my-ai-vectors'
try:
    client.create_vector_bucket(bucket_name)
    print(f"Created bucket: {bucket_name}")
except tos.exceptions.TosServerError as e:
    if e.code == 'ConflictException':
        print(f"Bucket {bucket_name} already exists")
    else:
        raise

# 3. Create vector index
index_name = 'embeddings-768d'
try:
    client.create_index(
        account_id=account_id,
        vector_bucket_name=bucket_name,
        index_name=index_name,
        data_type=tos.DataType.DataTypeFloat32,
        dimension=768,
        distance_metric=tos.DistanceMetricType.DistanceMetricCosine
    )
    print(f"Created index: {index_name}")
except tos.exceptions.TosServerError as e:
    if e.code == 'ConflictException':
        print(f"Index {index_name} already exists")
    else:
        raise

print("Setup complete!")
```

---

## Semantic Search System

### Build a Document Search System

```python
# Step 1: Prepare and index documents
def index_documents(client, bucket_name, account_id, index_name, documents):
    """
    Index a collection of documents for semantic search.

    Args:
        documents: List of dicts with 'id', 'title', 'content' keys
    """
    vectors = []

    for doc in documents:
        # Generate embedding (use your embedding model)
        embedding = generate_embedding(doc['content'])

        # Create vector with metadata
        vector = tos.models2.Vector(
            key=doc['id'],
            data=tos.models2.VectorData(float32=embedding),
            metadata={
                'title': doc['title'],
                'content_preview': doc['content'][:500],
                'category': doc.get('category', 'general')
            }
        )
        vectors.append(vector)

        # Batch insert every 500 vectors
        if len(vectors) >= 500:
            client.put_vectors(
                vector_bucket_name=bucket_name,
                account_id=account_id,
                index_name=index_name,
                vectors=vectors
            )
            print(f"Indexed {len(vectors)} documents")
            vectors = []

    # Insert remaining vectors
    if vectors:
        client.put_vectors(
            vector_bucket_name=bucket_name,
            account_id=account_id,
            index_name=index_name,
            vectors=vectors
        )
        print(f"Indexed {len(vectors)} documents")

# Step 2: Search documents
def search_documents(client, bucket_name, account_id, index_name, query, top_k=5):
    """
    Search for documents similar to the query.
    """
    # Generate query embedding
    query_embedding = generate_embedding(query)
    query_vector = tos.models2.VectorData(float32=query_embedding)

    # Search
    results = client.query_vectors(
        vector_bucket_name=bucket_name,
        account_id=account_id,
        index_name=index_name,
        query_vector=query_vector,
        top_k=top_k,
        return_distance=True,
        return_metadata=True
    )

    # Format results
    search_results = []
    for vec in results.vectors:
        search_results.append({
            'id': vec.key,
            'title': vec.metadata.get('title'),
            'preview': vec.metadata.get('content_preview'),
            'similarity_score': 1 - vec.distance,  # Convert distance to similarity
            'category': vec.metadata.get('category')
        })

    return search_results

# Usage example
documents = [
    {'id': 'doc-1', 'title': 'AI Introduction', 'content': '...', 'category': 'tech'},
    {'id': 'doc-2', 'title': 'ML Basics', 'content': '...', 'category': 'tech'},
]

index_documents(client, bucket_name, account_id, index_name, documents)
results = search_documents(client, bucket_name, account_id, index_name, "machine learning")

for result in results:
    print(f"{result['title']}: {result['similarity_score']:.3f}")
```

---


## RAG (Retrieval Augmented Generation)

### Build a RAG System

```python
def rag_query(client, bucket_name, account_id, index_name, question, llm_client):
    """
    Answer questions using RAG pattern.
    
    Args:
        question: User's question
        llm_client: Your LLM client (e.g., OpenAI, Claude)
    """
    # Step 1: Convert question to embedding
    question_embedding = generate_embedding(question)
    query_vector = tos.models2.VectorData(float32=question_embedding)
    
    # Step 2: Retrieve relevant documents
    search_results = client.query_vectors(
        vector_bucket_name=bucket_name,
        account_id=account_id,
        index_name=index_name,
        query_vector=query_vector,
        top_k=3,
        return_metadata=True
    )
    
    # Step 3: Build context from retrieved documents
    context_parts = []
    for i, vec in enumerate(search_results.vectors):
        context_parts.append(
            f"Document {i+1}:\n{vec.metadata.get('content', '')}"
        )
    context = "\n\n".join(context_parts)
    
    # Step 4: Generate answer with LLM
    prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""
    
    answer = llm_client.generate(prompt)
    
    return {
        'answer': answer,
        'sources': [vec.key for vec in search_results.vectors],
        'context': context
    }

# Usage
result = rag_query(
    client, bucket_name, account_id, index_name,
    "What is vector database?",
    llm_client
)
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

---


## Recommendation System

### Build a Product Recommendation System

```python
def recommend_products(client, bucket_name, account_id, index_name, 
                      user_preference_vector, filters=None, top_k=10):
    """
    Recommend products based on user preferences.
    
    Args:
        user_preference_vector: User's preference embedding
        filters: Optional metadata filters (e.g., category, price range)
        top_k: Number of recommendations
    """
    # Build filter if provided
    filter_query = None
    if filters:
        filter_query = {"$and": [filters]} if isinstance(filters, dict) else filters
    
    # Query similar products
    results = client.query_vectors(
        vector_bucket_name=bucket_name,
        account_id=account_id,
        index_name=index_name,
        query_vector=tos.models2.VectorData(float32=user_preference_vector),
        top_k=top_k,
        filter=filter_query,
        return_distance=True,
        return_metadata=True
    )
    
    # Format recommendations
    recommendations = []
    for vec in results.vectors:
        recommendations.append({
            'product_id': vec.key,
            'name': vec.metadata.get('name'),
            'category': vec.metadata.get('category'),
            'price': vec.metadata.get('price'),
            'relevance_score': 1 - vec.distance
        })
    
    return recommendations

# Usage with filters
recommendations = recommend_products(
    client, bucket_name, account_id, 'products-index',
    user_preference_vector,
    filters={"category": "electronics", "price_range": "mid"},
    top_k=10
)
```

---


## Vector Data Maintenance

### Update Vectors Workflow

```python
def update_vectors(client, bucket_name, account_id, index_name, updates):
    """
    Update existing vectors with new embeddings.
    
    Args:
        updates: List of dicts with 'key', 'embedding', 'metadata'
    """
    # Step 1: Delete old vectors
    keys_to_delete = [update['key'] for update in updates]
    client.delete_vectors(
        vector_bucket_name=bucket_name,
        account_id=account_id,
        index_name=index_name,
        keys=keys_to_delete
    )
    print(f"Deleted {len(keys_to_delete)} vectors")

    # Step 2: Insert new vectors
    new_vectors = []
    for update in updates:
        vector = tos.models2.Vector(
            key=update['key'],
            data=tos.models2.VectorData(float32=update['embedding']),
            metadata=update.get('metadata', {})
        )
        new_vectors.append(vector)

    client.put_vectors(
        vector_bucket_name=bucket_name,
        account_id=account_id,
        index_name=index_name,
        vectors=new_vectors
    )
    print(f"Updated {len(new_vectors)} vectors")

# Usage
updates = [
    {
        'key': 'doc-1',
        'embedding': new_embedding_1,
        'metadata': {'version': 'v2', 'updated_at': '2026-01-29'}
    }
]
update_vectors(client, bucket_name, account_id, index_name, updates)
```

### Batch Processing with Pagination

```python
def process_all_vectors(client, bucket_name, account_id, index_name, 
                       process_fn, batch_size=100):
    """
    Process all vectors in an index with pagination.
    
    Args:
        process_fn: Function to process each batch of vectors
    """
    next_token = None
    total_processed = 0
    
    while True:
        # List vectors
        result = client.list_vectors(
            vector_bucket_name=bucket_name,
            index_name=index_name,
            account_id=account_id,
            max_results=batch_size,
            next_token=next_token,
            return_metadata=True
        )
        
        # Process batch
        process_fn(result.vectors)
        total_processed += len(result.vectors)
        print(f"Processed {total_processed} vectors")
        
        # Check if more pages exist
        if not result.next_token:
            break
        next_token = result.next_token
    
    return total_processed

# Usage
def analyze_batch(vectors):
    for vec in vectors:
        print(f"Vector {vec.key}: {vec.metadata}")

total = process_all_vectors(
    client, bucket_name, account_id, index_name,
    analyze_batch
)
print(f"Total vectors processed: {total}")
```
