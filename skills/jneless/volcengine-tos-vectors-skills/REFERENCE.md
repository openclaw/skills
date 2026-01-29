# TOS Vectors API Reference

Complete API reference for TOS Vectors Python SDK operations.

## Table of Contents

- [Client Initialization](#client-initialization)
- [Vector Bucket Operations](#vector-bucket-operations)
- [Vector Index Operations](#vector-index-operations)
- [Vector Data Operations](#vector-data-operations)
- [Policy Management](#policy-management)
- [Error Handling](#error-handling)

---

## Client Initialization

### VectorClient

```python
tos.VectorClient(ak, sk, endpoint, region)
```

**Parameters:**
- `ak` (str): Access Key ID
- `sk` (str): Secret Access Key
- `endpoint` (str): Service endpoint URL
- `region` (str): Region identifier (e.g., 'cn-beijing')

**Example:**
```python
import tos
client = tos.VectorClient(
    ak='your-access-key',
    sk='your-secret-key',
    endpoint='https://tosvectors-cn-beijing.volces.com',
    region='cn-beijing'
)
```

---

## Vector Bucket Operations

### create_vector_bucket

Create a new vector bucket.

```python
client.create_vector_bucket(vector_bucket_name)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name (3-32 chars, lowercase, numbers, hyphens)

**Returns:**
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

**Constraints:**
- Max 100 buckets per account
- Name must be unique within region and account
- Cannot start or end with hyphen

**Example:**
```python
result = client.create_vector_bucket('my-vector-bucket')
print(f"Created bucket, Request ID: {result.request_id}")
```

---

### delete_vector_bucket

Delete an empty vector bucket.

```python
client.delete_vector_bucket(vector_bucket_name, account_id)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name to delete
- `account_id` (str): Account ID for authorization

**Returns:**
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

**Prerequisites:**
- Bucket must be empty (all indexes deleted)

**Example:**
```python
result = client.delete_vector_bucket('my-vector-bucket', account_id)
```

---

### get_vector_bucket

Get detailed information about a vector bucket.

```python
client.get_vector_bucket(vector_bucket_name, account_id)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `account_id` (str): Account ID

**Returns:**
- `vector_bucket` (object):
  - `vector_bucket_name` (str): Bucket name
  - `vector_bucket_trn` (str): TRN identifier
  - `creation_time` (int): Unix timestamp
  - `project_name` (str): Project name
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

**Example:**
```python
result = client.get_vector_bucket('my-vector-bucket', account_id)
print(f"Bucket: {result.vector_bucket.vector_bucket_name}")
print(f"Created: {result.vector_bucket.creation_time}")
```

---

### list_vector_buckets

List vector buckets with pagination.

```python
client.list_vector_buckets(max_results=100, next_token=None, prefix=None)
```

**Parameters:**
- `max_results` (int, optional): Max items per page (1-500, default: 100)
- `next_token` (str, optional): Pagination token
- `prefix` (str, optional): Filter by name prefix (1-63 chars)

**Returns:**
- `vector_buckets` (list): List of bucket summaries
- `next_token` (str): Token for next page (if more results exist)
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

**Example:**
```python
# First page
page1 = client.list_vector_buckets(max_results=10)
for bucket in page1.vector_buckets:
    print(bucket.vector_bucket_name)

# Next page
if page1.next_token:
    page2 = client.list_vector_buckets(
        max_results=10,
        next_token=page1.next_token
    )
```

---

## Vector Index Operations

### create_index

Create a vector index within a bucket.

```python
client.create_index(
    account_id,
    vector_bucket_name,
    index_name,
    data_type,
    dimension,
    distance_metric,
    metadata_configuration=None
)
```

**Parameters:**
- `account_id` (str): Account ID
- `vector_bucket_name` (str): Bucket name
- `index_name` (str): Index name (3-63 chars)
- `data_type` (DataType): `tos.DataType.DataTypeFloat32`
- `dimension` (int): Vector dimension (1-4096)
- `distance_metric` (DistanceMetricType):
  - `tos.DistanceMetricType.DistanceMetricEuclidean`
  - `tos.DistanceMetricType.DistanceMetricCosine`
- `metadata_configuration` (dict, optional): Metadata config

**Returns:**
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

**Example:**
```python
result = client.create_index(
    account_id=account_id,
    vector_bucket_name='my-bucket',
    index_name='embeddings-768d',
    data_type=tos.DataType.DataTypeFloat32,
    dimension=768,
    distance_metric=tos.DistanceMetricType.DistanceMetricCosine
)
```

---

### delete_index

Delete a vector index.

```python
client.delete_index(vector_bucket_name, account_id, index_name)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `account_id` (str): Account ID
- `index_name` (str): Index name to delete

**Returns:**
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

---

### get_index

Get detailed information about a vector index.

```python
client.get_index(vector_bucket_name, account_id, index_name)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `account_id` (str): Account ID
- `index_name` (str): Index name

**Returns:**
- `index` (object): Index details with dimension, metric, etc.
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

---

### list_indexes

List indexes in a bucket with pagination.

```python
client.list_indexes(
    vector_bucket_name,
    account_id,
    max_results=100,
    next_token=None,
    prefix=None
)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `account_id` (str): Account ID
- `max_results` (int, optional): Max items per page (1-500, default: 100)
- `next_token` (str, optional): Pagination token
- `prefix` (str, optional): Filter by name prefix

**Returns:**
- `indexes` (list): List of index summaries
- `next_token` (str): Token for next page

---

## Vector Data Operations

### put_vectors

Batch insert vectors into an index.

```python
client.put_vectors(
    vector_bucket_name=vector_bucket_name,
    account_id=account_id,
    index_name=index_name,
    vectors=vectors
)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `account_id` (str): Account ID
- `index_name` (str): Index name
- `vectors` (list): List of Vector objects (1-500 items)

**Vector Object:**
```python
tos.models2.Vector(
    key='unique-id',
    data=tos.models2.VectorData(float32=[...]),
    metadata={'key': 'value'}  # Optional
)
```

**Returns:**
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

**Example:**
```python
vectors = [
    tos.models2.Vector(
        key='doc-1',
        data=tos.models2.VectorData(float32=[0.1] * 768),
        metadata={'title': 'Document 1'}
    )
]
result = client.put_vectors(
    vector_bucket_name='my-bucket',
    account_id=account_id,
    index_name='my-index',
    vectors=vectors
)
```

---

### query_vectors

Search for similar vectors using KNN.

```python
client.query_vectors(
    vector_bucket_name,
    account_id,
    index_name,
    query_vector,
    top_k,
    return_distance=False,
    return_metadata=False,
    filter=None
)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `account_id` (str): Account ID
- `index_name` (str): Index name
- `query_vector` (VectorData): Query vector
- `top_k` (int): Number of results (1-30)
- `return_distance` (bool): Include distance scores
- `return_metadata` (bool): Include metadata
- `filter` (dict): Metadata filter (e.g., `{"$and": [{"category": "tech"}]}`)

**Returns:**
- `vectors` (list): List of matching vectors with key, distance, metadata
- `request_id` (str): Request identifier

**Example:**
```python
query_vector = tos.models2.VectorData(float32=[0.1] * 768)
results = client.query_vectors(
    vector_bucket_name='my-bucket',
    account_id=account_id,
    index_name='my-index',
    query_vector=query_vector,
    top_k=5,
    return_distance=True,
    return_metadata=True
)

for vec in results.vectors:
    print(f"Key: {vec.key}, Distance: {vec.distance}")
```

---

### get_vectors

Retrieve vectors by their keys.

```python
client.get_vectors(
    vector_bucket_name,
    account_id,
    index_name,
    keys,
    return_data=False,
    return_metadata=False
)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `account_id` (str): Account ID
- `index_name` (str): Index name
- `keys` (list): List of vector keys (1-100 items)
- `return_data` (bool): Include vector data
- `return_metadata` (bool): Include metadata

**Returns:**
- `vectors` (list): List of vectors
- `request_id` (str): Request identifier

**Example:**
```python
result = client.get_vectors(
    vector_bucket_name='my-bucket',
    account_id=account_id,
    index_name='my-index',
    keys=['doc-1', 'doc-2'],
    return_data=True,
    return_metadata=True
)
```

---

### delete_vectors

Delete vectors by their keys.

```python
client.delete_vectors(vector_bucket_name, account_id, index_name, keys)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `account_id` (str): Account ID
- `index_name` (str): Index name
- `keys` (list): List of vector keys to delete (1-100 items)

**Returns:**
- `request_id` (str): Request identifier
- `status_code` (int): HTTP status code

**Example:**
```python
result = client.delete_vectors(
    vector_bucket_name='my-bucket',
    account_id=account_id,
    index_name='my-index',
    keys=['doc-1', 'doc-2']
)
```

---

### list_vectors

List vectors in an index with pagination.

```python
client.list_vectors(
    vector_bucket_name,
    index_name,
    account_id,
    max_results=500,
    next_token=None,
    return_data=False,
    return_metadata=False
)
```

**Parameters:**
- `vector_bucket_name` (str): Bucket name
- `index_name` (str): Index name
- `account_id` (str): Account ID
- `max_results` (int): Max items (1-1000, default: 500)
- `next_token` (str): Pagination token
- `return_data` (bool): Include vector data
- `return_metadata` (bool): Include metadata

**Returns:**
- `vectors` (list): List of vectors
- `next_token` (str): Token for next page

**Example:**
```python
result = client.list_vectors(
    vector_bucket_name='my-bucket',
    index_name='my-index',
    account_id=account_id,
    max_results=100,
    return_metadata=True
)
```

---


## Policy Management

### put_vector_bucket_policy

Set IAM policy for a vector bucket.

```python
client.put_vector_bucket_policy(vector_bucket_name, account_id, policy)
```

### get_vector_bucket_policy

Get IAM policy for a vector bucket.

```python
client.get_vector_bucket_policy(vector_bucket_name, account_id)
```

### delete_vector_bucket_policy

Delete IAM policy for a vector bucket.

```python
client.delete_vector_bucket_policy(vector_bucket_name, account_id)
```

---

## Error Handling

### Exception Types

**TosClientError**: Client-side errors
```python
except tos.exceptions.TosClientError as e:
    print(f'Client error: {e.message}, Cause: {e.cause}')
```

**TosServerError**: Server-side errors
```python
except tos.exceptions.TosServerError as e:
    print(f'Error code: {e.code}')
    print(f'Request ID: {e.request_id}')
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| AccessDeniedException | 403 | Access denied |
| ConflictException | 409 | Resource already exists |
| InternalServerException | 500 | Internal server error |
| ServiceQuotaExceededException | 402 | Quota exceeded |
| ServiceUnavailableException | 503 | Service unavailable |
| TooManyRequestsException | 429 | Rate limited |
| ValidationException | 400 | Invalid parameters |
