# test_ai.py
# This tests the complete flow - search + AI answer

import sys
import os
sys.path.append(os.path.abspath('.'))

from retrieval.search_engine import hybrid_search
from ai_layer.reasoning_engine import ask_regumind

# Ask a real question about our BRD document
query = "What are the hallucination detection requirements in ReguMind?"

print("="*50)
print("REGUMIND - FULL RAG PIPELINE TEST")
print("="*50)
print(f"Question: {query}")

# Step 1 - Retrieve relevant chunks
print("\n[STEP 1] Searching for relevant chunks...")
chunks = hybrid_search(query, top_k=3)

# Step 2 - Generate grounded answer
print("\n[STEP 2] Generating grounded answer...")
result = ask_regumind(query, chunks)

# Show the answer
print("\n" + "="*50)
print("ANSWER:")
print("="*50)
print(result['answer'])
print("\n" + "="*50)
print(f"Sources used: {result['sources_used']}")
print(f"Chunks retrieved: {result['chunks_retrieved']}")
print(f"Model used: {result['model_used']}")