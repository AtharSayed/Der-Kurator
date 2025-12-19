# loaders/docx_loader.py
from docx import Document
from loaders.base_loader import BaseLoader

class DocxLoader(BaseLoader):
    def load(self, file_path):
        doc = Document(file_path)
        documents = []

        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():
                documents.append({
                    "content": para.text.strip(),
                    "metadata": {
                        "source": file_path,
                        "type": "docx",
                        "unit": "paragraph",
                        "index": i
                    }
                })
        return documents