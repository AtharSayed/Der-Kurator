# ingest.py
import os
from sentence_transformers import SentenceTransformer
import faiss
import pickle


from loaders.txt_loader import TxtLoader
from loaders.docx_loader import DocxLoader
from loaders.pdf_loader import PdfLoader
from loaders.pptx_loader import PptxLoader
from preprocessing.cleaner import clean_text
from preprocessing.chunker import chunk_text

model = SentenceTransformer("all-MiniLM-L6-v2")

loaders = {
    ".txt": TxtLoader(),
    ".docx": DocxLoader(),
    ".pdf": PdfLoader(),
    ".pptx": PptxLoader()
}

all_chunks = []
all_metadata = []

for file in os.listdir("data/raw"):
    ext = os.path.splitext(file)[1]
    loader = loaders.get(ext)

    if loader:
        docs = loader.load(f"data/raw/{file}")
        for d in docs:
            clean = clean_text(d["content"])
            chunks = chunk_text(clean)
            for c in chunks:
                all_chunks.append(c)
                all_metadata.append(d["metadata"])

embeddings = model.encode(all_chunks, show_progress_bar=True)


index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)


faiss.write_index(index, "embeddings/vector_store/index.faiss")
pickle.dump((all_chunks, all_metadata), open("embeddings/vector_store/data.pkl", "wb"))
print("Ingestion complete. Vector store and data saved.")
