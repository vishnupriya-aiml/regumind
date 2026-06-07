# test_loader.py
# This file tests our document loader with a real PDF

from ingestion.document_loader import load_document

# Load the BRD PDF from our data folder
file_path = "data/Business Requirements Document (BRD).pdf"

# Call our loader
text, metadata = load_document(file_path)

# Print the metadata
print("\n--- METADATA ---")
for key, value in metadata.items():
    print(f"{key}: {value}")

# Print first 500 characters of extracted text
print("\n--- FIRST 500 CHARACTERS OF EXTRACTED TEXT ---")
print(text[:500])

print("\n--- TOTAL TEXT LENGTH ---")
print(f"Total characters extracted: {len(text)}")