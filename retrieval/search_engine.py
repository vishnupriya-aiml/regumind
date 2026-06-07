# retrieval/search_engine.py
# This file handles hybrid search - combining vector and keyword search
# It finds the most relevant chunks for any user query

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.embedder import generate_embedding
from retrieval.vector_store import search_similar, client, COLLECTION_NAME
from rank_bm25 import BM25Okapi


def get_all_chunks():
    """
    Retrieves all stored chunks from Qdrant.
    We need these for BM25 keyword search.
    """
    # Scroll through all points in the collection
    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )

    chunks = []
    for point in results:
        chunks.append({
            "text": point.payload['text'],
            "source_filename": point.payload['source_filename'],
            "chunk_id": point.payload['chunk_id'],
            "chunk_index": point.payload['chunk_index']
        })

    return chunks


def vector_search(query, top_k=5):
    """
    Searches using semantic similarity.
    Converts query to embedding then finds similar vectors.
    """
    print(f"Running vector search for: '{query}'")

    # Convert query to embedding
    query_embedding = generate_embedding(query)

    # Search Qdrant for similar chunks
    results = search_similar(query_embedding, top_k=top_k)

    print(f"Vector search found {len(results)} results")
    return results


def bm25_search(query, chunks, top_k=5):
    """
    Searches using BM25 keyword matching.
    Good for finding exact terms and technical codes.
    """
    print(f"Running BM25 keyword search for: '{query}'")

    if not chunks:
        print("No chunks available for BM25 search")
        return []

    # Tokenize all chunk texts into word lists
    tokenized_chunks = [chunk['text'].lower().split() for chunk in chunks]

    # Build BM25 index
    bm25 = BM25Okapi(tokenized_chunks)

    # Search with tokenized query
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    # Get top_k results sorted by score
    top_indices = sorted(range(len(scores)),
                        key=lambda i: scores[i],
                        reverse=True)[:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "score": float(scores[idx]),
                "text": chunks[idx]['text'],
                "source_filename": chunks[idx]['source_filename'],
                "chunk_id": chunks[idx]['chunk_id'],
                "chunk_index": chunks[idx]['chunk_index']
            })

    print(f"BM25 search found {len(results)} results")
    return results


def hybrid_search(query, top_k=5):
    """
    Combines vector search and BM25 search results.
    This gives us the best of semantic and keyword search.

    The final score for each chunk is:
    (vector_score * 0.7) + (bm25_score * 0.3)

    We weight vector search higher because meaning
    is usually more important than exact keyword match.
    """
    print(f"\nRunning hybrid search for: '{query}'")
    print("-" * 40)

    # Run both searches
    vector_results = vector_search(query, top_k=top_k)
    all_chunks = get_all_chunks()
    bm25_results = bm25_search(query, all_chunks, top_k=top_k)

    # Combine results using a dictionary keyed by chunk_id
    combined = {}

    # Add vector search results with 0.7 weight
    for result in vector_results:
        chunk_id = result['chunk_id']
        combined[chunk_id] = {
            "text": result['text'],
            "source_filename": result['source_filename'],
            "chunk_id": chunk_id,
            "vector_score": result['score'],
            "bm25_score": 0.0,
            "hybrid_score": result['score'] * 0.7
        }

    # Add or update with BM25 results with 0.3 weight
    # Normalize BM25 scores to 0-1 range first
    if bm25_results:
        max_bm25 = max(r['score'] for r in bm25_results)
        for result in bm25_results:
            chunk_id = result['chunk_id']
            normalized_score = result['score'] / max_bm25 if max_bm25 > 0 else 0

            if chunk_id in combined:
                combined[chunk_id]['bm25_score'] = normalized_score
                combined[chunk_id]['hybrid_score'] += normalized_score * 0.3
            else:
                combined[chunk_id] = {
                    "text": result['text'],
                    "source_filename": result['source_filename'],
                    "chunk_id": chunk_id,
                    "vector_score": 0.0,
                    "bm25_score": normalized_score,
                    "hybrid_score": normalized_score * 0.3
                }

    # Sort by hybrid score and return top_k
    sorted_results = sorted(combined.values(),
                           key=lambda x: x['hybrid_score'],
                           reverse=True)[:top_k]

    print(f"Hybrid search complete. Returning {len(sorted_results)} results")
    return sorted_results


if __name__ == "__main__":
    # Test our search engine with a real query
    query = "What are the hallucination detection requirements?"

    print("="*50)
    print("TESTING HYBRID SEARCH ENGINE")
    print("="*50)

    results = hybrid_search(query, top_k=3)

    print("\n--- SEARCH RESULTS ---")
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"  Source: {result['source_filename']}")
        print(f"  Hybrid Score: {result['hybrid_score']:.4f}")
        print(f"  Vector Score: {result['vector_score']:.4f}")
        print(f"  BM25 Score: {result['bm25_score']:.4f}")
        print(f"  Text preview: {result['text'][:200]}")