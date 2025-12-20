# ingest.py (Updated: Structure-Aware + Variant-Aware Hybrid Chunking using Unstructured)

import os
import copy
from sentence_transformers import SentenceTransformer
import faiss
import pickle

# Unstructured.io for advanced structure-aware, document-type-aware partitioning
from unstructured.partition.auto import partition

# Optional: Keep your existing cleaner if needed (recommended)
from preprocessing.cleaner import clean_text

# Embedding model (excellent for technical docs)
model = SentenceTransformer("all-mpnet-base-v2")

all_chunks = []
all_metadata = []

raw_data_path = "data/raw"
os.makedirs(raw_data_path, exist_ok=True)

print("Starting structure-aware ingestion with Unstructured.io...")

for file in os.listdir(raw_data_path):
    file_path = os.path.join(raw_data_path, file)
    filename = os.path.basename(file_path)

    print(f"Processing {filename}...")

    try:
        # Auto-partition: detects file type and applies best strategy
        # - PDF: hi-res layout detection (tables, headings, columns)
        # - PPTX: slide-by-slide, preserves titles, bullets
        # - DOCX: section/heading aware
        # - TXT: paragraph aware
        elements = partition(filename=file_path)

    except Exception as e:
        print(f"Error partitioning {filename}: {str(e)}")
        continue

    for elem_idx, element in enumerate(elements):
        # Extract clean text from element
        raw_text = element.text
        if not raw_text or not raw_text.strip():
            continue

        cleaned_text = clean_text(raw_text.strip())
        if not cleaned_text:
            continue

        # Create chunk (each structural element becomes a coherent chunk)
        all_chunks.append(cleaned_text)

        # Build rich metadata
        metadata = {
            "source": filename,
            "element_type": element.category,  # e.g., Title, NarrativeText, Table, ListItem, Image, etc.
            "element_index": elem_idx,
            "chunk_char_count": len(cleaned_text),
        }
        text_lower = cleaned_text.lower()

        if "gt3" in text_lower:
            metadata["variant"] = "GT3"
        elif "carrera s" in text_lower:
            metadata["variant"] = "Carrera S"
        elif "turbo s" in text_lower:
            metadata["variant"] = "Turbo S"
        elif "gts" in text_lower:
            metadata["variant"] = "GTS"

        # Add page number if available (PDFs)
        if hasattr(element, "metadata") and getattr(element.metadata, "page_number", None) is not None:
            metadata["page"] = element.metadata.page_number

        # Add slide number if available (PPTX)
        if hasattr(element, "metadata") and getattr(element.metadata, "slide_number", None) is not None:
            metadata["slide"] = element.metadata.slide_number

        # Optional: Add coordinates or other layout info if needed later
        # metadata["coordinates"] = element.metadata.coordinates if available

        all_metadata.append(copy.deepcopy(metadata))

print(f"Successfully generated {len(all_chunks)} structure-aware chunks from {len(os.listdir(raw_data_path))} files.")

# Generate embeddings and build FAISS index
if all_chunks:
    print("Encoding chunks with all-mpnet-base-v2...")
    embeddings = model.encode(
        all_chunks,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity (normalized)
    index.add(embeddings.astype('float32'))

    # Save vector store
    os.makedirs("embeddings/vector_store", exist_ok=True)
    faiss.write_index(index, "embeddings/vector_store/index.faiss")

    with open("embeddings/vector_store/data.pkl", "wb") as f:
        pickle.dump((all_chunks, all_metadata), f)

    print("Ingestion complete! Hybrid structure-aware vector store saved.")
    print("Your RAG system now uses advanced layout and document-type aware chunking.")
else:
    print("No valid chunks generated. Please check your documents in data/raw/.")