import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """Configuration settings for the PDF parser and Pinecone integration."""
    
    # Pinecone settings
    pinecone_api_key: str = ""  # Set via .env file
    pinecone_environment: str = ""  # Set via .env file (e.g., "gcp-starter")
    index_name: str = "contract-clauses"
    
    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Search settings
    default_top_k: int = 3
    
    # Chunking settings
    clause_pattern: str = r"(?:^|\n)(\d+(\.\d+)*\s+[A-Z][^\n]+)"
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        return cls(
            pinecone_api_key=os.getenv("PINECONE_API_KEY", cls.pinecone_api_key),
            pinecone_environment=os.getenv("PINECONE_ENV", cls.pinecone_environment),
            index_name=os.getenv("INDEX_NAME", cls.index_name),
            embedding_model=os.getenv("EMBEDDING_MODEL", cls.embedding_model),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", cls.embedding_dimension)),
            default_top_k=int(os.getenv("DEFAULT_TOP_K", cls.default_top_k))
        )

# Global config instance
config = Config.from_env() 