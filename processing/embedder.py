# processing/embedder.py
# This file converts text chunks into embeddings (lists of numbers)
# We use a free local model called BGE that runs on your computer

from sentence_transformers import SentenceTransformer
import numpy as np

# Load the embedding model
# This model runs locally on your computer - no API key needed
# It will download automatically the first time (about 400MB)
print("Loading embedding model... (first time may take a few minutes to download)")
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
print("Embedding model loaded successfully!")


def generate_embedding(text):
    """
    Converts a single piece of text into an embedding.
    Returns a list of numbers (vector) representing the meaning.
    """
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_for_chunks(chunks):
    """
    Takes a list of chunk objects and adds an embedding to each one.
    Returns the same chunks but now each has an 'embedding' field.
    """
    print(f"Generating embeddings for {len(chunks)} chunks...")

    # Extract just the text from each chunk for batch processing
    texts = [chunk['text'] for chunk in chunks]

    # Generate all embeddings at once (faster than one by one)
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    # Add the embedding back to each chunk object
    for index, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[index].tolist()
        chunk['embedding_dimension'] = len(embeddings[index])

    print(f"Successfully generated {len(chunks)} embeddings!")
    print(f"Each embedding has {len(embeddings[0])} dimensions")

    return chunks


if __name__ == "__main__":
    # Quick test with a sample sentence
    print("\nTesting embedding generation...")
    sample_text = "ReguMind is an enterprise regulatory intelligence platform"
    embedding = generate_embedding(sample_text)
    print(f"Sample text: {sample_text}")
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 numbers: {embedding[:5]}")
    print("\nEmbedder is ready!")