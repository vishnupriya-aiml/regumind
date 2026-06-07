# ingestion/pipeline.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.document_loader import load_document
from processing.chunker import process_document
from processing.embedder import generate_embeddings_for_chunks
from retrieval.vector_store import create_collection, store_chunks, get_collection_info


def ingest_document(file_path):
    """
    Master function that takes a file path and runs it through
    the complete ingestion pipeline end to end.
    """
    print("\n" + "="*50)
    print(f"STARTING INGESTION: {file_path}")
    print("="*50)

    print("\n[STEP 1/4] Loading document...")
    text, metadata = load_document(file_path)
    print(f"Loaded: {metadata['filename']}")

    print("\n[STEP 2/4] Cleaning and chunking text...")
    chunks = process_document(text, metadata)
    print(f"Created {len(chunks)} chunks")

    print("\n[STEP 3/4] Generating embeddings...")
    chunks_with_embeddings = generate_embeddings_for_chunks(chunks)
    print(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")

    print("\n[STEP 4/4] Storing in vector database...")
    create_collection()
    store_chunks(chunks_with_embeddings)

    info = get_collection_info()
    print("\n" + "="*50)
    print("INGESTION COMPLETE!")
    print(f"Document: {metadata['filename']}")
    print(f"Chunks stored: {len(chunks)}")
    print(f"Total vectors in database: {info['total_vectors']}")
    print("="*50)

    return {
        "filename": metadata['filename'],
        "chunks_created": len(chunks),
        "total_vectors": info['total_vectors'],
        "chunks_stored": len(chunks),
        "success": True
    }


def run_pipeline(file_path):
    """
    Alias for ingest_document — called by the API.
    """
    try:
        result = ingest_document(file_path)
        return {
            "success": True,
            "chunks_stored": result['chunks_stored'],
            "filename": result['filename']
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def ingest_folder(folder_path):
    """
    Ingests all supported documents from a folder.
    """
    supported_extensions = ['.pdf', '.docx', '.txt']
    files_processed = 0
    files_failed = 0

    print(f"\nScanning folder: {folder_path}")
    for filename in os.listdir(folder_path):
        extension = os.path.splitext(filename)[1].lower()
        if extension in supported_extensions:
            file_path = os.path.join(folder_path, filename)
            try:
                ingest_document(file_path)
                files_processed += 1
            except Exception as e:
                print(f"Failed to ingest {filename}: {e}")
                files_failed += 1

    print(f"\nFolder ingestion complete!")
    print(f"Successfully processed: {files_processed} files")
    print(f"Failed: {files_failed} files")


if __name__ == "__main__":
    ingest_document("data/Business Requirements Document (BRD).pdf")