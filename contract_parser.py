from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from pdf_extractor import PDFExtractor
from text_chunker import TextChunker, TextChunk
from embedding_service import EmbeddingService
from pinecone_service import PineconeService
from config import config

logger = logging.getLogger(__name__)

class ContractParser:
    """ 
    orchestrates the entire pipeline:
    1. Extract text from PDF
    2. Chunk text into clauses
    3. Generate embeddings
    4. Store in Pinecone
    5. Enable semantic search
    """
    
    def __init__(self, 
                 pdf_extractor: Optional[PDFExtractor] = None,
                 chunker: Optional[TextChunker] = None,
                 embedding_service: Optional[EmbeddingService] = None,
                 pinecone_service: Optional[PineconeService] = None):
        """
        Initialize the contract parser with all required services.
        
        Args:
            pdf_extractor: PDF text extraction service
            chunker: Text chunking service
            embedding_service: Embedding generation service
            pinecone_service: Pinecone vector database service
        """
        self.pdf_extractor = pdf_extractor or PDFExtractor()
        self.chunker = chunker or TextChunker()
        self.embedding_service = embedding_service or EmbeddingService()
        self.pinecone_service = pinecone_service or PineconeService()
        
        logger.info("ContractParser initialized successfully")
    
    def process_contract(self, pdf_path: str, chunking_strategy: str = "clauses") -> Dict[str, Any]:
        """
        Process a contract PDF through the entire pipeline.
        
        Args:
            pdf_path: Path to the PDF file
            chunking_strategy: Strategy for chunking ("clauses", "sentences", "paragraphs")
            
        Returns:
            Dictionary with processing results and statistics
        """
        logger.info(f"Processing contract: {pdf_path}")
        
        try:
            # Step 1: Extract text from PDF
            text = self.pdf_extractor.extract_text(pdf_path)
            logger.info(f"Extracted {len(text)} characters from PDF")
            
            # Step 2: Chunk text
            chunks = self._chunk_text(text, chunking_strategy)
            chunk_stats = self.chunker.get_chunk_statistics(chunks)
            logger.info(f"Created {len(chunks)} chunks using {chunking_strategy} strategy")
            
            # Step 3: Generate embeddings
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.encode_batch(chunk_texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Step 4: Upload to Pinecone
            success = self.pinecone_service.upsert_chunks(chunks, embeddings)
            
            if not success:
                raise Exception("Failed to upload chunks to Pinecone")
            
            # Step 5: Get index statistics
            index_stats = self.pinecone_service.get_index_stats()
            
            return {
                "success": True,
                "pdf_path": pdf_path,
                "text_length": len(text),
                "chunks_created": len(chunks),
                "embeddings_generated": len(embeddings),
                "chunk_statistics": chunk_stats,
                "index_statistics": index_stats,
                "chunking_strategy": chunking_strategy
            }
            
        except Exception as e:
            logger.error(f"Error processing contract: {e}")
            return {
                "success": False,
                "error": str(e),
                "pdf_path": pdf_path
            }
    
    def _chunk_text(self, text: str, strategy: str) -> List[TextChunk]:
        """
        Chunk text using the specified strategy.
        
        Args:
            text: Text to chunk
            strategy: Chunking strategy
            
        Returns:
            List of TextChunk objects
        """
        if strategy == "clauses":
            return self.chunker.chunk_by_clauses(text)
        elif strategy == "sentences":
            return self.chunker.chunk_by_sentences(text)
        elif strategy == "paragraphs":
            return self.chunker.chunk_by_paragraphs(text)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
    
    def search_contract(self, query: str, top_k: int = None, 
                       filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search the contract using natural language queries.
        
        Args:
            query: Natural language query
            top_k: Number of top results to return
            filter_dict: Optional filter criteria for Pinecone
            
        Returns:
            List of search results with metadata
        """
        logger.info(f"Searching contract with query: {query}")
        
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.encode_text(query)
            
            # Search in Pinecone
            results = self.pinecone_service.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching contract: {e}")
            return []
    
    def get_contract_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the processed contract data.
        
        Returns:
            Dictionary with contract statistics
        """
        try:
            index_stats = self.pinecone_service.get_index_stats()
            return {
                "index_statistics": index_stats,
                "embedding_dimension": self.embedding_service.get_embedding_dimension(),
                "embedding_model": self.embedding_service.model_name
            }
        except Exception as e:
            logger.error(f"Error getting contract statistics: {e}")
            return {}
    
    def clear_contract_data(self) -> bool:
        """
        Clear all contract data from Pinecone.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Clearing all contract data from Pinecone")
        return self.pinecone_service.delete_all_vectors()
    
    def batch_process_contracts(self, pdf_paths: List[str], 
                               chunking_strategy: str = "clauses") -> List[Dict[str, Any]]:
        """
        Process multiple contracts in batch.
        
        Args:
            pdf_paths: List of PDF file paths
            chunking_strategy: Strategy for chunking
            
        Returns:
            List of processing results for each contract
        """
        logger.info(f"Batch processing {len(pdf_paths)} contracts")
        
        results = []
        for i, pdf_path in enumerate(pdf_paths):
            logger.info(f"Processing contract {i+1}/{len(pdf_paths)}: {pdf_path}")
            result = self.process_contract(pdf_path, chunking_strategy)
            results.append(result)
            
            if not result["success"]:
                logger.warning(f"Failed to process contract {i+1}: {result.get('error', 'Unknown error')}")
        
        successful = sum(1 for r in results if r["success"])
        logger.info(f"Batch processing complete: {successful}/{len(pdf_paths)} contracts processed successfully")
        
        return results
    
    def validate_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Validate a PDF file before processing.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Check if file exists
            if not Path(pdf_path).exists():
                return {"valid": False, "error": "File does not exist"}
            
            # Check if it's a PDF
            if not pdf_path.lower().endswith('.pdf'):
                return {"valid": False, "error": "File is not a PDF"}
            
            # Try to extract text to validate PDF structure
            text = self.pdf_extractor.extract_text(pdf_path)
            
            if not text.strip():
                return {"valid": False, "error": "PDF appears to be empty or unreadable"}
            
            return {
                "valid": True,
                "text_length": len(text),
                "page_count": self.pdf_extractor.get_page_count()
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)} 