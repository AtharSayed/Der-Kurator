# preprocessing/chunker.py
import re

def split_into_sentences(text: str):
    text = re.sub(r'\s+', ' ', text.strip())
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text: str, max_chunk_size: int = 800, sentence_overlap: int = 2):
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
            if len(sentence) > max_chunk_size:
                # Split long sentence into words if too long
                words = sentence.split()
                sub_sentences = []
                sub = ""
                for w in words:
                    if len(sub) + len(w) + 1 > max_chunk_size and sub:
                        sub_sentences.append(sub.strip())
                        sub = w
                    else:
                        sub += " " + w if sub else w
                if sub:
                    sub_sentences.append(sub.strip())
                sentence = ' '.join(sub_sentences)  # Rejoin, but now it's split if needed
                sentences[i:i+1] = sub_sentences  # Replace original long sentence

            added_length = len(sentence) + (1 if current_chunk else 0)

            if current_chunk and current_length + added_length > max_chunk_size:
                break

            current_chunk.append(sentence)
            current_length += added_length
            i += 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        i = max(start_idx + len(current_chunk) - sentence_overlap, start_idx + 1)  # Avoid infinite

    return chunks