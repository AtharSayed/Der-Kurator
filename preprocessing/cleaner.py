# preprocessing/cleaner.py
import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove non-printable
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t ')

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove repeated punctuation/symbols (e.g., ----- or ****)
    text = re.sub(r'([^\w\s])\1{2,}', r'\1', text)

    # Optional: remove isolated numbers/symbols if noisy
    # text = re.sub(r'\b\d+\b', '', text)  # Uncomment if numbers are noise

    # Trim leading/trailing punctuation
    text = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', text)

    return text.strip()