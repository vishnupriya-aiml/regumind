# processing/chunker.py
# This file cleans extracted text and splits it into chunks
# Each chunk will later be converted into an embedding

import re


def clean_text(text):
    """
    Cleans raw extracted text by fixing spacing issues,
    removing extra blank lines, and stripping junk characters.
    """
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)

    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)

    # Remove lines that are just whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]

    # Join everything back together cleanly
    cleaned = ' '.join(lines)

    return cleaned.strip()


def split_into_chunks(text, chunk_size=500, overlap=50):
    """
    Splits cleaned text into chunks of approximately chunk_size words.

    overlap means the last 50 words of one chunk are repeated
    at the start of the next chunk. This helps the AI understand
    context that spans across chunk boundaries.

    Think of it like how book chapters sometimes recap
    what happened at the end of the previous chapter.
    """
    # Split text into individual words
    words = text.split()

    chunks = []
    start = 0

    while start < len(words):
        # Take chunk_size words starting from current position
        end = start + chunk_size

        # Grab those words and join them back into a string
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)

        chunks.append(chunk_text)

        # Move forward by chunk_size minus overlap
        # This creates the overlapping effect
        start += chunk_size - overlap

    return chunks


def process_document(text, metadata, chunk_size=500, overlap=50):
    """
    Master function that cleans text and splits into chunks.
    Each chunk gets its own metadata so we always know
    which document and position it came from.
    """
    print(f"Processing document: {metadata['filename']}")

    # Step 1 - Clean the text
    cleaned_text = clean_text(text)
    print(f"Text cleaned. Length before: {len(text)} | After: {len(cleaned_text)}")

    # Step 2 - Split into chunks
    chunks = split_into_chunks(cleaned_text, chunk_size, overlap)
    print(f"Created {len(chunks)} chunks from document")

    # Step 3 - Attach metadata to each chunk
    chunk_objects = []
    for index, chunk_text in enumerate(chunks):
        chunk = {
            "chunk_id": f"{metadata['filename']}_chunk_{index}",
            "text": chunk_text,
            "chunk_index": index,
            "total_chunks": len(chunks),
            "source_filename": metadata['filename'],
            "source_file_type": metadata['file_type'],
            "uploaded_at": metadata['uploaded_at'],
            "word_count": len(chunk_text.split())
        }
        chunk_objects.append(chunk)

    print(f"Chunking complete for: {metadata['filename']}")
    return chunk_objects


if __name__ == "__main__":
    print("Chunker module is ready!")
    print("Functions available: clean_text, split_into_chunks, process_document")