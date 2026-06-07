# retrieval/vector_store.py
# This file handles all communication with Qdrant vector database
# It creates collections, stores chunks, and searches for similar content

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

# Connect to Qdrant running on localhost port 6333
import os
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
client = QdrantClient(host=QDRANT_HOST, port=6333)

# Name of our collection in Qdrant
COLLECTION_NAME = "regumind_documents"

# Size of our embeddings (BGE small model produces 384 dimensions)
EMBEDDING_DIMENSION = 384


def create_collection():
    """
    Creates the main collection in Qdrant if it does not exist yet.
    This is like creating a table in a regular database.
    """
    # Check if collection already exists
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists. Skipping creation.")
        return

    # Create new collection with cosine similarity
    # Cosine similarity measures the angle between two vectors
    # Vectors pointing in similar directions = similar meaning
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSION,
            distance=Distance.COSINE
        )
    )
    print(f"Collection '{COLLECTION_NAME}' created successfully!")


def store_chunks(chunks):
    """
    Stores a list of chunks with their embeddings into Qdrant.
    Each chunk becomes one point in the collection.
    """
    print(f"Storing {len(chunks)} chunks into Qdrant...")

    # Convert chunks into Qdrant PointStruct objects
    points = []
    for chunk in chunks:
        point = PointStruct(
            # Each point needs a unique ID
            id=str(uuid.uuid4()),
            # The vector is the embedding we generated
            vector=chunk['embedding'],
            # The payload stores the text and metadata
            payload={
                "chunk_id": chunk['chunk_id'],
                "text": chunk['text'],
                "chunk_index": chunk['chunk_index'],
                "total_chunks": chunk['total_chunks'],
                "source_filename": chunk['source_filename'],
                "source_file_type": chunk['source_file_type'],
                "uploaded_at": chunk['uploaded_at'],
                "word_count": chunk['word_count']
            }
        )
        points.append(point)

    # Upload all points to Qdrant in one batch
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Successfully stored {len(chunks)} chunks into Qdrant!")


def search_similar(query_embedding, top_k=5):
    """
    Searches Qdrant for chunks most similar to the query embedding.
    Returns the top_k most relevant chunks.
    """
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True
    )

    # Format results into clean dictionaries
    formatted = []
    for result in results:
        formatted.append({
            "score": result.score,
            "text": result.payload['text'],
            "source_filename": result.payload['source_filename'],
            "chunk_id": result.payload['chunk_id'],
            "chunk_index": result.payload['chunk_index']
        })

    return formatted

def get_collection_info():
    try:
        count_result = client.count(
            collection_name=COLLECTION_NAME,
            exact=True
        )
        total = count_result.count
    except Exception:
        total = 0
    return {
        "name": COLLECTION_NAME,
        "total_vectors": total,
        "status": "green"
    }

if __name__ == "__main__":
    print("Testing Qdrant connection...")
    create_collection()
    info = get_collection_info()
    print(f"Collection info: {info}")
    print("Vector store is ready!")