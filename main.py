import logging
import sys
from pathlib import Path
from typing import List

from contract_parser import ContractParser
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('contract_parser.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    logging.getLogger().setLevel(numeric_level)

def process_single_contract(pdf_path: str, chunking_strategy: str = "clauses") -> dict:
    """
    Process a single contract and return results.
    
    Args:
        pdf_path: Path to the PDF file
        chunking_strategy: Strategy for chunking text
        
    Returns:
        Processing results
    """
    logger.info(f"Processing single contract: {pdf_path}")
    
    # Initialize the contract parser
    parser = ContractParser()
    
    # Validate the PDF first
    validation = parser.validate_pdf(pdf_path)
    if not validation["valid"]:
        logger.error(f"PDF validation failed: {validation['error']}")
        return {"success": False, "error": validation["error"]}
    
    # Process the contract
    result = parser.process_contract(pdf_path, chunking_strategy)
    
    if result["success"]:
        logger.info(f"Successfully processed contract: {result['chunks_created']} chunks created")
        logger.info(f"Chunk statistics: {result['chunk_statistics']}")
    else:
        logger.error(f"Failed to process contract: {result['error']}")
    
    return result

def search_contract_clauses(query: str, top_k: int = 5) -> List[dict]:
    """
    Search for specific clauses in the processed contract.
    
    Args:
        query: Natural language query
        top_k: Number of top results to return
        
    Returns:
        List of search results
    """
    logger.info(f"Searching for: {query}")
    
    parser = ContractParser()
    results = parser.search_contract(query, top_k=top_k)
    
    if results:
        logger.info(f"Found {len(results)} relevant clauses:")
        for i, result in enumerate(results, 1):
            score = result['score']
            heading = result['metadata']['heading']
            content = result['metadata']['content'][:200] + "..." if len(result['metadata']['content']) > 200 else result['metadata']['content']
            
            print(f"\n{i}. Score: {score:.3f}")
            print(f"   Heading: {heading}")
            print(f"   Content: {content}")
    else:
        logger.info("No relevant clauses found")
    
    return results

def batch_process_contracts(pdf_directory: str, chunking_strategy: str = "clauses") -> List[dict]:
    """
    Process multiple contracts in a directory.
    
    Args:
        pdf_directory: Directory containing PDF files
        chunking_strategy: Strategy for chunking text
        
    Returns:
        List of processing results
    """
    logger.info(f"Batch processing contracts in: {pdf_directory}")
    
    # Find all PDF files in the directory
    pdf_dir = Path(pdf_directory)
    if not pdf_dir.exists():
        logger.error(f"Directory does not exist: {pdf_directory}")
        return []
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in: {pdf_directory}")
        return []
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Initialize parser and process all contracts
    parser = ContractParser()
    results = parser.batch_process_contracts(
        [str(f) for f in pdf_files], 
        chunking_strategy
    )
    
    # Print summary
    successful = sum(1 for r in results if r["success"])
    logger.info(f"Batch processing summary: {successful}/{len(pdf_files)} contracts processed successfully")
    
    return results

def get_system_statistics() -> dict:
    """
    Get statistics about the current system state.
    
    Returns:
        System statistics
    """
    logger.info("Getting system statistics")
    
    parser = ContractParser()
    stats = parser.get_contract_statistics()
    
    print("\n=== System Statistics ===")
    print(f"Embedding Model: {stats.get('embedding_model', 'Unknown')}")
    print(f"Embedding Dimension: {stats.get('embedding_dimension', 'Unknown')}")
    print(f"Index Statistics: {stats.get('index_statistics', {})}")
    
    return stats

def interactive_search():
    """
    Run an interactive search session.
    """
    logger.info("Starting interactive search session")
    
    parser = ContractParser()
    
    print("\n=== Interactive Contract Search ===")
    print("Type 'quit' to exit, 'stats' for statistics")
    
    while True:
        try:
            query = input("\nEnter your search query: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'stats':
                get_system_statistics()
                continue
            elif not query:
                continue
            
            results = parser.search_contract(query, top_k=3)
            
            if results:
                print(f"\nFound {len(results)} relevant clauses:")
                for i, result in enumerate(results, 1):
                    score = result['score']
                    heading = result['metadata']['heading']
                    content = result['metadata']['content'][:150] + "..." if len(result['metadata']['content']) > 150 else result['metadata']['content']
                    
                    print(f"\n{i}. Score: {score:.3f}")
                    print(f"   Heading: {heading}")
                    print(f"   Content: {content}")
            else:
                print("No relevant clauses found.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error during interactive search: {e}")
            print(f"Error: {e}")

def main():
    setup_logging("INFO")
    
    print("=== Simple Contract Parser ===")
    
    # Configuration - choose your mode
    PROCESSING_MODE = "batch"  # Options: "single", "batch", "directory"
    
    # Single file processing
    single_pdf_path = "test_pdfs/loan_contract.pdf"
    
    # Batch processing - specific files
    batch_pdf_paths = [
        "test_pdfs/loan_contract.pdf",
        "test_pdfs/trust_contract.pdf", 
        "test_pdfs/credit_contract.pdf"
    ]
    
    # Directory processing
    pdf_directory = "test_pdfs"
    
    if PROCESSING_MODE == "single":
        # Single file processing
        print(f"\n1. Processing single contract: {single_pdf_path}")
        
        if not Path(single_pdf_path).exists():
            print(f"PDF file not found: {single_pdf_path}")
            return
            
        result = process_single_contract(single_pdf_path, chunking_strategy="sentences")
        
        if result["success"]:
            print(f"Successfully processed contract: {result['chunks_created']} chunks created")
            
            # Search examples
            print("\n2. Searching for termination clauses...")
            search_contract_clauses("When can I terminate the contract?", top_k=3)
            
            print("\n3. Searching for payment terms...")
            search_contract_clauses("What are the payment terms?", top_k=3)
            
            # System stats
            print("\n4. Getting system statistics...")
            get_system_statistics()
            
            # Interactive search
            print("\n5. Starting interactive search...")
            interactive_search()
        else:
            print(f"Failed to process contract: {result['error']}")
    
    elif PROCESSING_MODE == "batch":
        # Batch processing - specific files
        print(f"\n1. Batch processing {len(batch_pdf_paths)} contracts...")
        
        # Check if files exist
        missing_files = []
        for pdf_path in batch_pdf_paths:
            if not Path(pdf_path).exists():
                missing_files.append(pdf_path)
        
        if missing_files:
            print(f"Missing files:")
            for file in missing_files:
                print(f"  - {file}")
            return
        
        # Initialize parser and process all contracts
        from contract_parser import ContractParser
        parser = ContractParser()
        results = parser.batch_process_contracts(batch_pdf_paths, chunking_strategy="sentences")
        
        successful = sum(1 for r in results if r["success"])
        print(f"Successfully processed {successful}/{len(batch_pdf_paths)} contracts!")
        
        if successful > 0:
            # Search examples
            print("\n2. Searching for termination clauses...")
            search_contract_clauses("When can I terminate the contract?", top_k=3)
            
            print("\n3. Searching for payment terms...")
            search_contract_clauses("What are the payment terms?", top_k=3)
            
            # System stats
            print("\n4. Getting system statistics...")
            get_system_statistics()
            
            # Interactive search
            print("\n5. Starting interactive search...")
            interactive_search()
    
    elif PROCESSING_MODE == "directory":
        # Directory processing - all PDFs in folder
        print(f"\n1. Processing all PDFs in directory: {pdf_directory}")
        
        if not Path(pdf_directory).exists():
            print(f"Directory not found: {pdf_directory}")
            return
        
        results = batch_process_contracts(pdf_directory, chunking_strategy="sentences")
        
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        print(f"Successfully processed {successful}/{total} contracts!")
        
        if successful > 0:
            # Search examples
            print("\n2. Searching for termination clauses...")
            search_contract_clauses("When can I terminate the contract?", top_k=3)
            
            print("\n3. Searching for payment terms...")
            search_contract_clauses("What are the payment terms?", top_k=3)
            
            # System stats
            print("\n4. Getting system statistics...")
            get_system_statistics()
            
            # Interactive search
            print("\n5. Starting interactive search...")
            interactive_search()
    
    else:
        print("Invalid PROCESSING_MODE. Use 'single', 'batch', or 'directory'")
        return

if __name__ == "__main__":
    main()