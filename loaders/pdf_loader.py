# loaders/pdf_loader.py
from pypdf import PdfReader
from loaders.base_loader import BaseLoader

class PdfLoader(BaseLoader):
    def load(self, file_path):
        reader = PdfReader(file_path)
        documents = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                documents.append({
                    "content": text.strip(),
                    "metadata": {
                        "source": file_path,
                        "type": "pdf",
                        "unit": "page",
                        "index": i + 1
                    }
                })
        return documents
