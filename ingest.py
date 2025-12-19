# ingest.py
import os
import copy
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle

from loaders.txt_loader import TxtLoader
from loaders.docx_loader import DocxLoader
from loaders.pdf_loader import PdfLoader
from loaders.pptx_loader import PptxLoader
from preprocessing.cleaner import clean_text
from preprocessing.chunker import chunk_text

# Better embedding model
model = SentenceTransformer("all-mpnet-base-v2")

loaders = {
    ".txt": TxtLoader(),
    ".docx": DocxLoader(),
    ".pdf": PdfLoader(),
    ".pptx": PptxLoader()
}

all_chunks = []
all_metadata = []

raw_data_path = "data/raw"
os.makedirs(raw_data_path, exist_ok=True)

for file in os.listdir(raw_data_path):
    file_path = os.path.join(raw_data_path, file)
    ext = os.path.splitext(file)[1].lower()

    loader = loaders.get(ext)
    if not loader:
        print(f"Skipping unsupported file: {file}")
        continue

    try:
        print(f"Processing {file}...")
        docs = loader.load(file_path)
    except Exception as e:
        print(f"Error loading {file}: {str(e)}")
        continue

    for doc in docs:
        cleaned_text = clean_text(doc["content"])
        if not cleaned_text:
            continue

        chunks = chunk_text(cleaned_text, max_chunk_size=800, sentence_overlap=2)

        for chunk_idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            metadata = copy.deepcopy(doc["metadata"])
            metadata["chunk_index"] = chunk_idx
            metadata["chunk_char_count"] = len(chunk)
            all_metadata.append(metadata)

print(f"Generated {len(all_chunks)} chunks from {len(os.listdir(raw_data_path))} files.")

if all_chunks:
    embeddings = model.encode(
        all_chunks,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype('float32'))

    os.makedirs("embeddings/vector_store", exist_ok=True)

    faiss.write_index(index, "embeddings/vector_store/index.faiss")
    with open("embeddings/vector_store/data.pkl", "wb") as f:
        pickle.dump((all_chunks, all_metadata), f)

    print("Ingestion complete! Vector store saved.")
else:
    print("No chunks generated. Check your data files.")