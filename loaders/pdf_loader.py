# loaders/pdf_loader.py
import fitz  # PyMuPDF
from loaders.base_loader import BaseLoader

class PdfLoader(BaseLoader):
    def load(self, file_path):
        """
        Extract text from each page using PyMuPDF for higher quality and speed.
        """
        doc = fitz.open(file_path)
        documents = []

        for i, page in enumerate(doc):
            text = page.get_text("text")  # Plain text, preserves reading order better
            if text and text.strip():
                documents.append({
                    "content": text.strip(),
                    "metadata": {
                        "source": file_path,
                        "type": "pdf",
                        "unit": "page",
                        "index": i + 1
                    }
                })

        doc.close()
        return documents