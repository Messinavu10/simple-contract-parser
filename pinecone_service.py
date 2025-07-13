from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional, Tuple
import uuid
import logging
from config import config
from text_chunker import TextChunk

logger = logging.getLogger(__name__)

class PineconeService:
    """Handles all Pinecone vector database operations."""
    
    def __init__(self, api_key: str = None, environment: str = None, index_name: str = None):
        """
        Initialize the Pinecone service.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the index to use
        """
        self.api_key = api_key or config.pinecone_api_key
        self.environment = environment or config.pinecone_environment
        self.index_name = index_name or config.index_name
        self.pc = None
        self.index = None
        self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone and create index if needed."""
        try:
            logger.info("Initializing Pinecone")
            
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                
                # Create index with serverless spec for free plan
                self.pc.create_index(
                    name=self.index_name,
                    dimension=config.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info("Index created successfully")
            else:
                logger.info(f"Using existing index: {self.index_name}")
            
            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            logger.info("Pinecone service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    def upsert_chunks(self, chunks: List[TextChunk], embeddings: List[List[float]]) -> bool:
        """
        Upload text chunks and their embeddings to Pinecone.
        
        Args:
            chunks: List of TextChunk objects
            embeddings: List of embeddings corresponding to chunks
            
        Returns:
            True if successful, False otherwise
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        if not chunks:
            logger.warning("No chunks to upsert")
            return True
        
        try:
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = str(uuid.uuid4())
                metadata = {
                    "heading": chunk.heading,
                    "content": chunk.content,
                    "chunk_id": chunk.chunk_id,
                    "start_position": chunk.start_position,
                    "end_position": chunk.end_position
                }
                
                vectors.append((vector_id, embedding, metadata))
                
                # Log progress for large batches
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(chunks)} chunks")
            
            # Upsert in batches to avoid rate limits
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                logger.debug(f"Upserted batch {i//batch_size + 1}")
            
            logger.info(f"Successfully upserted {len(chunks)} chunks to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting chunks to Pinecone: {e}")
            return False
    
    def search(self, query_embedding: List[float], top_k: int = None, 
               filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Pinecone.
        
        Args:
            query_embedding: Query embedding
            top_k: Number of top results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of search results with metadata
        """
        if top_k is None:
            top_k = config.default_top_k
        
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            logger.info(f"Search returned {len(results['matches'])} results")
            return results['matches']
            
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []
    
    def delete_vectors(self, vector_ids: List[str]) -> bool:
        """
        Delete specific vectors from the index.
        
        Args:
            vector_ids: List of vector IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not vector_ids:
            return True
        
        try:
            self.index.delete(ids=vector_ids)
            logger.info(f"Deleted {len(vector_ids)} vectors from Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from Pinecone: {e}")
            return False
    
    def delete_all_vectors(self) -> bool:
        """
        Delete all vectors from the index.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.index.delete(delete_all=True)
            logger.info("Deleted all vectors from Pinecone index")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting all vectors from Pinecone: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Pinecone index.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
    
    def fetch_vectors(self, vector_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch specific vectors by their IDs.
        
        Args:
            vector_ids: List of vector IDs to fetch
            
        Returns:
            List of vectors with metadata
        """
        if not vector_ids:
            return []
        
        try:
            results = self.index.fetch(ids=vector_ids)
            return list(results['vectors'].values())
            
        except Exception as e:
            logger.error(f"Error fetching vectors from Pinecone: {e}")
            return []