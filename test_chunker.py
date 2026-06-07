# test_chunker.py
# This tests our cleaning and chunking with the real BRD document

from ingestion.document_loader import load_document
from processing.chunker import process_document

# Step 1 - Load the PDF
file_path = "data/Business Requirements Document (BRD).pdf"
text, metadata = load_document(file_path)

# Step 2 - Clean and chunk it
chunks = process_document(text, metadata)

# Step 3 - Show results
print("\n--- CHUNKING RESULTS ---")
print(f"Total chunks created: {len(chunks)}")

print("\n--- FIRST CHUNK ---")
print(f"Chunk ID: {chunks[0]['chunk_id']}")
print(f"Word count: {chunks[0]['word_count']}")
print(f"Text preview: {chunks[0]['text'][:300]}")

print("\n--- SECOND CHUNK ---")
print(f"Chunk ID: {chunks[1]['chunk_id']}")
print(f"Word count: {chunks[1]['word_count']}")
print(f"Text preview: {chunks[1]['text'][:300]}")

print("\n--- LAST CHUNK ---")
print(f"Chunk ID: {chunks[-1]['chunk_id']}")
print(f"Word count: {chunks[-1]['word_count']}")
print(f"Text preview: {chunks[-1]['text'][:300]}")