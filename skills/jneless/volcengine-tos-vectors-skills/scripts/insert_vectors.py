#!/usr/bin/env python3
"""
Insert sample vectors into TOS Vectors index.

Example usage:
    python insert_vectors.py
"""

import os
import sys
import tos


def generate_dummy_embedding(text, dimension=768):
    """Generate a dummy embedding for demonstration."""
    import hashlib
    hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
    return [(hash_val % 1000) / 1000.0] * dimension


def main():
    # Get credentials
    ak = os.getenv('TOS_ACCESS_KEY')
    sk = os.getenv('TOS_SECRET_KEY')
    account_id = os.getenv('TOS_ACCOUNT_ID')

    if not all([ak, sk, account_id]):
        print("Error: Missing environment variables")
        sys.exit(1)

    # Configuration
    endpoint = 'https://tosvectors-cn-beijing.volces.com'
    region = 'cn-beijing'
    bucket_name = 'my-vectors'
    index_name = 'embeddings-768d'

    # Initialize client
    client = tos.VectorClient(ak, sk, endpoint, region)

    # Sample documents
    documents = [
        {'id': 'doc-1', 'title': 'Introduction to AI', 'content': 'Artificial intelligence basics'},
        {'id': 'doc-2', 'title': 'Machine Learning Guide', 'content': 'ML algorithms and techniques'},
        {'id': 'doc-3', 'title': 'Deep Learning', 'content': 'Neural networks and deep learning'},
    ]

    # Create vectors
    vectors = []
    for doc in documents:
        embedding = generate_dummy_embedding(doc['content'])
        vector = tos.models2.Vector(
            key=doc['id'],
            data=tos.models2.VectorData(float32=embedding),
            metadata={'title': doc['title'], 'content': doc['content']}
        )
        vectors.append(vector)

    # Insert vectors
    print(f"Inserting {len(vectors)} vectors...")
    try:
        client.put_vectors(
            vector_bucket_name=bucket_name,
            account_id=account_id,
            index_name=index_name,
            vectors=vectors
        )
        print(f"✓ Successfully inserted {len(vectors)} vectors")
        for doc in documents:
            print(f"  - {doc['id']}: {doc['title']}")
    except tos.exceptions.TosServerError as e:
        print(f"✗ Error: {e.message}")
        sys.exit(1)


if __name__ == '__main__':
    main()
