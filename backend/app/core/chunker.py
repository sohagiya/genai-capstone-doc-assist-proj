"""Text chunking with token-aware splitting"""
import re
from typing import List, Dict, Optional
from backend.app.utils.logger import logger


class TextChunker:
    """Chunk text into overlapping segments with token awareness"""

    def __init__(self, target_tokens: int = 500, overlap_tokens: int = 50):
        """
        Initialize chunker
        Args:
            target_tokens: Target chunk size in tokens (400-600 recommended)
            overlap_tokens: Overlap between chunks in tokens (10-20% of target)
        """
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens

        # Simple token estimation: ~4 characters per token on average
        self.chars_per_token = 4
        self.target_chars = target_tokens * self.chars_per_token
        self.overlap_chars = overlap_tokens * self.chars_per_token

    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text"""
        return len(text) // self.chars_per_token

    def split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraph boundaries"""
        # Split on double newlines or single newlines followed by indentation
        paragraphs = re.split(r'\n\s*\n|\n(?=\s{2,})', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Chunk text with overlap, preferring paragraph boundaries
        Returns list of chunk dicts with text, metadata, and positions
        """
        if not text or not text.strip():
            return []

        chunks = []
        paragraphs = self.split_by_paragraphs(text)

        if not paragraphs:
            paragraphs = [text]

        current_chunk = []
        current_size = 0
        chunk_id = 0
        start_pos = 0

        for para_idx, paragraph in enumerate(paragraphs):
            para_size = len(paragraph)
            para_tokens = self.estimate_tokens(paragraph)

            # If single paragraph exceeds target, split it
            if para_tokens > self.target_tokens * 1.5:
                # Save current chunk if exists
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_id, start_pos, metadata
                    ))
                    chunk_id += 1
                    current_chunk = []
                    current_size = 0

                # Split large paragraph by sentences
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                temp_chunk = []
                temp_size = 0

                for sent in sentences:
                    sent_size = len(sent)
                    if temp_size + sent_size > self.target_chars and temp_chunk:
                        # Save temp chunk
                        chunk_text = " ".join(temp_chunk)
                        chunks.append(self._create_chunk(
                            chunk_text, chunk_id, start_pos, metadata
                        ))
                        chunk_id += 1

                        # Overlap: keep last sentence
                        if self.overlap_chars > 0:
                            temp_chunk = [temp_chunk[-1]]
                            temp_size = len(temp_chunk[-1])
                        else:
                            temp_chunk = []
                            temp_size = 0

                        start_pos += len(chunk_text)

                    temp_chunk.append(sent)
                    temp_size += sent_size

                # Save remaining
                if temp_chunk:
                    chunk_text = " ".join(temp_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_id, start_pos, metadata
                    ))
                    chunk_id += 1
                    start_pos += len(chunk_text)

            else:
                # Normal paragraph processing
                if current_size + para_size > self.target_chars and current_chunk:
                    # Save current chunk
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_id, start_pos, metadata
                    ))
                    chunk_id += 1

                    # Overlap: keep last paragraph if small enough
                    if self.overlap_chars > 0 and len(current_chunk[-1]) <= self.overlap_chars:
                        current_chunk = [current_chunk[-1]]
                        current_size = len(current_chunk[-1])
                    else:
                        current_chunk = []
                        current_size = 0

                    start_pos += len(chunk_text)

                current_chunk.append(paragraph)
                current_size += para_size

        # Save final chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(self._create_chunk(
                chunk_text, chunk_id, start_pos, metadata
            ))

        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

    def _create_chunk(self, text: str, chunk_id: int, start_pos: int, metadata: Optional[Dict]) -> Dict:
        """Create a chunk dictionary with metadata"""
        chunk = {
            "chunk_id": chunk_id,
            "text": text,
            "start_pos": start_pos,
            "end_pos": start_pos + len(text),
            "token_count": self.estimate_tokens(text),
            "char_count": len(text)
        }

        # Add document metadata if provided
        if metadata:
            chunk["metadata"] = metadata

        return chunk
