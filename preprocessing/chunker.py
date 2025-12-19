# preprocessing/chunker.py
import re

def split_into_sentences(text: str):
    """
    Split text into sentences while handling common abbreviations.
    """
    text = re.sub(r'\s+', ' ', text.strip())
    # Split on .!? followed by whitespace, but not after known abbreviations
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text: str, max_chunk_size: int = 800, sentence_overlap: int = 2):
    """
    Semantic-aware chunking:
      - Split into sentences first to preserve meaning
      - Group sentences into chunks ≤ max_chunk_size characters
      - Overlap by a few sentences for context continuity
    
    Recommended max_chunk_size ≈ 800 chars ≈ 150–200 tokens for most models.
    """
    if not text:
        return []

    sentences = split_into_sentences(text)
    if not sentences:
        return []

    chunks = []
    i = 0
    while i < len(sentences):
        current_chunk = []
        current_length = 0
        start_idx = i

        while i < len(sentences):
            sentence = sentences[i]
            added_length = len(sentence) + (1 if current_chunk else 0)  # account for space

            # If adding this sentence would exceed limit and we already have content, stop
            if current_chunk and current_length + added_length > max_chunk_size:
                break

            current_chunk.append(sentence)
            current_length += added_length
            i += 1

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(chunk_text)

        # Overlap: step back by sentence_overlap sentences (but not before start)
        i = max(start_idx + len(current_chunk) - sentence_overlap, i - sentence_overlap)

        # Prevent infinite loop
        if len(current_chunk) == 0:
            i += 1

    return chunks