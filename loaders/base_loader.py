# loaders/base_loader.py
from abc import ABC, abstractmethod

class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> list[dict]:
        """
        Returns:
        [
          {
            "content": str,
            "metadata": {
                "source": str,
                "type": str,
                "unit": str,
                "index": int
            }
          }
        ]
        """
        pass
