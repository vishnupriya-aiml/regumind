# test_full_pipeline.py
# Tests the complete pipeline including hallucination detection

import sys
import os
sys.path.append(os.path.abspath('.'))

from retrieval.search_engine import hybrid_search
from ai_layer.reasoning_engine import ask_regumind
from hallucination.detector import detect_hallucination

def run_regumind(query):
    """
    Runs the complete ReguMind pipeline for a given query.
    Search → Answer → Verify
    """
    print("\n" + "="*60)
    print("REGUMIND - ENTERPRISE RAG PIPELINE")
    print("="*60)
    print(f"Question: {query}")

    # Step 1 - Hybrid Search
    print("\n[STEP 1/3] Searching documents...")
    chunks = hybrid_search(query, top_k=3)
    print(f"Found {len(chunks)} relevant chunks")

    # Step 2 - Generate Answer
    print("\n[STEP 2/3] Generating grounded answer...")
    result = ask_regumind(query, chunks)

    # Step 3 - Hallucination Detection
    print("\n[STEP 3/3] Verifying answer for hallucinations...")
    report = detect_hallucination(result['answer'], chunks)

    # Print complete results
    print("\n" + "="*60)
    print("FINAL ANSWER:")
    print("="*60)
    print(result['answer'])

    print("\n" + "="*60)
    print("VERIFICATION REPORT:")
    print("="*60)
    print(f"Confidence Score:     {report['confidence_score']:.2%}")
    print(f"Total Sentences:      {report['total_sentences']}")
    print(f"Supported:            {report['supported_count']}")
    print(f"Unsupported/Flagged:  {report['unsupported_count']}")
    print(f"Verdict:              {report['verdict']}")

    if report['unsupported_sentences']:
        print("\n⚠️  FLAGGED SENTENCES:")
        for sentence in report['unsupported_sentences']:
            print(f"  - {sentence}")
    else:
        print("\n✅ All sentences are supported by source documents!")

    print("\n" + "="*60)
    print(f"Sources: {result['sources_used']}")
    print(f"Model:   {result['model_used']}")
    print("="*60)

    return result, report


# Run with a real question
run_regumind("What are the success metrics for ReguMind?")