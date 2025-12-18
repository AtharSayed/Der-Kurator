# loaders/txt_loader.py
from loaders.base_loader import BaseLoader

class TxtLoader(BaseLoader):
    def load(self, file_path):
        documents = []
        with open(file_path, "r", encoding="utf-8") as f:
            paragraphs = f.read().split("\n\n")

        for i, para in enumerate(paragraphs):
            if para.strip():
                documents.append({
                    "content": para.strip(),
                    "metadata": {
                        "source": file_path,
                        "type": "txt",
                        "unit": "paragraph",
                        "index": i
                    }
                })
        return documents
