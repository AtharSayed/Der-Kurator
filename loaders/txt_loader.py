# loaders/txt_loader.py
from loaders.base_loader import BaseLoader

class TxtLoader(BaseLoader):
    def load(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Split on blank lines to get paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        documents = []
        for i, para in enumerate(paragraphs):
            documents.append({
                "content": para,
                "metadata": {
                    "source": file_path,
                    "type": "txt",
                    "unit": "paragraph",
                    "index": i
                }
            })
        return documents