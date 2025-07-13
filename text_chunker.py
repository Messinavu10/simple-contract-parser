import re
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import logging
from config import config

logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    heading: str
    content: str
    start_position: int
    end_position: int
    chunk_id: str = None
    
    def __post_init__(self):
        if self.chunk_id is None:
            self.chunk_id = f"{self.start_position}_{self.end_position}"

class TextChunker:
    """Handles chunking of text into logical sections like contract clauses."""
    
    def __init__(self, pattern: str = None):
        """
        Initialize the chunker.
        
        Args:
            pattern: Regex pattern for identifying clause boundaries
        """
        self.pattern = pattern or config.clause_pattern
        self.compiled_pattern = re.compile(self.pattern, re.MULTILINE)
    
    def chunk_by_clauses(self, text: str, max_chunk_size: int = 3000) -> List[TextChunk]:
        """
        Split text into clause-like chunks based on numbered headings.
        Falls back to sentence-based chunking if no clauses found.
        
        Args:
            text: The text to chunk
            max_chunk_size: Maximum characters per chunk (for fallback)
            
        Returns:
            List of TextChunk objects
        """
        logger.info("Chunking text into clauses")
        
        matches = list(self.compiled_pattern.finditer(text))
        chunks = []
        
        if not matches:
            logger.warning("No clause patterns found in text, falling back to sentence-based chunking")
            return self.chunk_by_sentences(text, max_chunk_size)
        
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            heading = match.group().strip()
            content = text[start:end].strip()
            
            # If a single clause is too large, split it further
            if len(content) > max_chunk_size:
                logger.info(f"Clause '{heading[:50]}...' is too large ({len(content)} chars), splitting further")
                sub_chunks = self.chunk_by_sentences(content, max_chunk_size)
                for j, sub_chunk in enumerate(sub_chunks):
                    sub_chunk.heading = f"{heading} - Part {j+1}"
                chunks.extend(sub_chunks)
            else:
                chunk = TextChunk(
                    heading=heading,
                    content=content,
                    start_position=start,
                    end_position=end
                )
                chunks.append(chunk)
            
            logger.debug(f"Created chunk: {heading[:50]}...")
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def chunk_by_sentences(self, text: str, max_chunk_size: int = 1000) -> List[TextChunk]:
        """
        Split text into chunks based on sentence boundaries.
        
        Args:
            text: The text to chunk
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of TextChunk objects
        """
        logger.info("Chunking text by sentences")
        
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append(TextChunk(
                    heading=f"Chunk {len(chunks) + 1}",
                    content=current_chunk.strip(),
                    start_position=current_start,
                    end_position=current_start + len(current_chunk)
                ))
                current_chunk = sentence
                current_start = current_start + len(current_chunk)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(TextChunk(
                heading=f"Chunk {len(chunks) + 1}",
                content=current_chunk.strip(),
                start_position=current_start,
                end_position=current_start + len(current_chunk)
            ))
        
        logger.info(f"Created {len(chunks)} sentence-based chunks")
        return chunks
    
    def chunk_by_paragraphs(self, text: str, max_chunk_size: int = 2000) -> List[TextChunk]:
        """
        Split text into chunks based on paragraph boundaries.
        
        Args:
            text: The text to chunk
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of TextChunk objects
        """
        logger.info("Chunking text by paragraphs")
        
        paragraphs = text.split('\n\n')
        chunks = []
        current_position = 0
        
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                current_position += len(paragraph) + 2  # +2 for '\n\n'
                continue
            
            # If paragraph is too large, split it into sentences
            if len(paragraph) > max_chunk_size:
                logger.info(f"Paragraph {i+1} is too large ({len(paragraph)} chars), splitting into sentences")
                sub_chunks = self.chunk_by_sentences(paragraph, max_chunk_size)
                for j, sub_chunk in enumerate(sub_chunks):
                    sub_chunk.heading = f"Paragraph {i+1} - Part {j+1}"
                chunks.extend(sub_chunks)
            else:
                chunks.append(TextChunk(
                    heading=f"Paragraph {i + 1}",
                    content=paragraph,
                    start_position=current_position,
                    end_position=current_position + len(paragraph)
                ))
            current_position += len(paragraph) + 2
        
        logger.info(f"Created {len(chunks)} paragraph-based chunks")
        return chunks
    
    def get_chunk_statistics(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of TextChunk objects
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {"total_chunks": 0, "avg_length": 0, "min_length": 0, "max_length": 0}
        
        lengths = [len(chunk.content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_length": sum(lengths) / len(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "total_characters": sum(lengths)
        }