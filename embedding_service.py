from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
import logging
from config import config

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Handles text embedding operations using SentenceTransformers."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        self.model_name = model_name or config.embedding_model
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the SentenceTransformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode_text(self, text: str) -> List[float]:
        """
        Encode a single text string into embeddings.
        
        Args:
            text: Text to encode
            
        Returns:
            List of float values representing the embedding
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            raise
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode multiple texts into embeddings (more efficient than individual calls).
        
        Args:
            texts: List of texts to encode
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text.strip()]
        if not valid_texts:
            return []
        
        try:
            embeddings = self.model.encode(valid_texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error encoding batch of texts: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        if self.model is None:
            raise ValueError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Normalize vectors
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            
            # Compute cosine similarity
            similarity = np.dot(vec1_norm, vec2_norm)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            raise
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]], 
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find the most similar embeddings to a query embedding.
        
        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with 'index' and 'similarity' keys
        """
        if not candidate_embeddings:
            return []
        
        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.compute_similarity(query_embedding, candidate)
            similarities.append({
                'index': i,
                'similarity': similarity
            })
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate that an embedding has the correct format and dimension.
        
        Args:
            embedding: Embedding to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(embedding, list):
            return False
        
        if not all(isinstance(x, (int, float)) for x in embedding):
            return False
        
        expected_dim = self.get_embedding_dimension()
        if len(embedding) != expected_dim:
            return False
        
        return True 