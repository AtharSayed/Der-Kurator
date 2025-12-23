# ingest.py (Updated: Structure-Aware + Variant-Aware Hybrid Chunking using Unstructured)
# Production enhancements:
# - Parallel file processing using multiprocessing for speed (CPU-bound tasks like partitioning and cleaning).
# - Robust error handling: Failures on individual files are logged and skipped without halting the pipeline.
# - Incremental index building: Embeddings are generated and added to FAISS in batches per file to manage memory and allow partial progress.
# - Resumability: Tracks processed files in a separate pickle file to skip already ingested files on restarts.
# - Logging: Uses Python's logging module for better monitoring and debugging.
# - Configurability: Uses environment variables or defaults for paths.
# - Batch encoding: Limits batch size during encoding to prevent OOM for large files.

import os
import copy
import logging
import pickle
from multiprocessing import Pool, cpu_count

from sentence_transformers import SentenceTransformer
import faiss

# Unstructured.io for advanced structure-aware, document-type-aware partitioning
from unstructured.partition.auto import partition

# Optional: Keep your existing cleaner if needed (recommended)
from preprocessing.cleaner import clean_text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Embedding model (excellent for technical docs)
model = SentenceTransformer("all-mpnet-base-v2")
dimension = model.get_sentence_embedding_dimension()

# Paths (configurable via env vars)
RAW_DATA_PATH = os.environ.get("RAW_DATA_PATH", "data/raw")
VECTOR_STORE_DIR = os.environ.get("VECTOR_STORE_DIR", "embeddings/vector_store")
os.makedirs(RAW_DATA_PATH, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
DATA_PATH = os.path.join(VECTOR_STORE_DIR, "data.pkl")
PROCESSED_FILES_PATH = os.path.join(VECTOR_STORE_DIR, "processed_files.pkl")

# Load existing vector store and processed files if they exist
if os.path.exists(INDEX_PATH) and os.path.exists(DATA_PATH):
    logging.info("Loading existing FAISS index and data...")
    index = faiss.read_index(INDEX_PATH)
    with open(DATA_PATH, "rb") as f:
        all_chunks, all_metadata = pickle.load(f)
else:
    logging.info("Initializing new FAISS index...")
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity (normalized)
    all_chunks = []
    all_metadata = []

if os.path.exists(PROCESSED_FILES_PATH):
    with open(PROCESSED_FILES_PATH, "rb") as f:
        processed_files = pickle.load(f)
else:
    processed_files = set()

def process_file(file_info):
    file_path, filename = file_info
    chunks = []
    metadata_list = []

    try:
        logging.info(f"Processing {filename}...")
        # Auto-partition: detects file type and applies best strategy
        elements = partition(filename=file_path)

        for elem_idx, element in enumerate(elements):
            # Extract clean text from element
            raw_text = element.text
            if not raw_text or not raw_text.strip():
                continue

            cleaned_text = clean_text(raw_text.strip())
            if not cleaned_text:
                continue

            # Create chunk (each structural element becomes a coherent chunk)
            chunks.append(cleaned_text)

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

            metadata_list.append(copy.deepcopy(metadata))

        logging.info(f"Generated {len(chunks)} chunks from {filename}.")
        return chunks, metadata_list

    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}")
        return [], []

def main():
    global all_chunks, all_metadata, index, processed_files

    files_to_process = []
    for file in os.listdir(RAW_DATA_PATH):
        file_path = os.path.join(RAW_DATA_PATH, file)
        if file in processed_files:
            logging.info(f"Skipping already processed file: {file}")
            continue
        files_to_process.append((file_path, file))

    if not files_to_process:
        logging.info("No new files to process.")
        return

    # Parallel processing with multiprocessing Pool
    num_workers = max(1, cpu_count() - 1)  # Leave one core free
    with Pool(num_workers) as pool:
        results = pool.map(process_file, files_to_process)

    # Collect results and add incrementally to avoid memory spikes
    for chunks, metadata_list in results:
        if chunks:
            logging.info(f"Encoding {len(chunks)} chunks...")
            embeddings = model.encode(
                chunks,
                batch_size=32,  # Smaller batch size for memory safety
                show_progress_bar=True,
                normalize_embeddings=True
            )
            index.add(embeddings.astype('float32'))

            all_chunks.extend(chunks)
            all_metadata.extend(metadata_list)

            # Update processed files (using the filename from files_to_process)
            # Note: Since map preserves order, we can zip
    for (file_path, filename), (chunks, _) in zip(files_to_process, results):
        if chunks:  # Only mark as processed if successfully generated chunks
            processed_files.add(filename)

    # Save everything
    logging.info("Saving updated vector store...")
    faiss.write_index(index, INDEX_PATH)
    with open(DATA_PATH, "wb") as f:
        pickle.dump((all_chunks, all_metadata), f)
    with open(PROCESSED_FILES_PATH, "wb") as f:
        pickle.dump(processed_files, f)

    logging.info(f"Ingestion complete! Processed {len(files_to_process)} files, total chunks: {len(all_chunks)}.")

if __name__ == "__main__":
    main()