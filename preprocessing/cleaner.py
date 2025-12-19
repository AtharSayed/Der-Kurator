# preprocessing/cleaner.py
import re

def clean_text(text: str) -> str:
    """
    Clean raw extracted text for better embedding quality.
    """
    if not text:
        return ""

    # Remove non-printable characters except common whitespace
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t ')

    # Normalize whitespace (multiple spaces, newlines, tabs → single space)
    text = re.sub(r'\s+', ' ', text)

    # Optional: remove URLs if they are noisy (uncomment if needed)
    # text = re.sub(r'http[s]?://\S+', '', text)

    # Trim leading/trailing punctuation that stands alone
    text = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', text)

    return text.strip()