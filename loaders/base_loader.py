# loaders/base_loader.py
from abc import ABC, abstractmethod

class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> list[dict]:
        """
        Load a document and return a list of segments.
        
        Returns:
            [
              {
                "content": str,
                "metadata": {
                    "source": str,    # full file path
                    "type": str,      # file extension like "pdf"
                    "unit": str,      # "page", "paragraph", "slide", etc.
                    "index": int      # index of the unit in the original document
                }
              }
            ]
        """
        pass