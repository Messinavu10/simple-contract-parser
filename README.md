# Contract Parser

A clean, modular system for extracting text from contract PDFs, chunking into clauses, generating embeddings, and enabling semantic search using Pinecone.

## Requirements

- Python 3.8+
- Pinecone account and API key
- Internet connection (for downloading embedding models)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pdf-parser
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional):
   ```bash
   export PINECONE_API_KEY="your-api-key"
   export PINECONE_ENV="your-environment"
   export INDEX_NAME="contract-clauses"
   ```

## Usage

### Basic Usage

```python
from contract_parser import ContractParser

# Initialize the parser
parser = ContractParser()

# Process a contract
result = parser.process_contract("path/to/contract.pdf")

# Search for specific clauses
results = parser.search_contract("When can I terminate the contract?")
```

### Advanced Usage

```python
from contract_parser import ContractParser
from pdf_extractor import PDFExtractor
from text_chunker import TextChunker
from embedding_service import EmbeddingService
from pinecone_service import PineconeService

# Customize individual components
pdf_extractor = PDFExtractor()
chunker = TextChunker(pattern=r"custom-pattern")
embedding_service = EmbeddingService(model_name="all-mpnet-base-v2")
pinecone_service = PineconeService(index_name="custom-index")

# Initialize with custom components
parser = ContractParser(
    pdf_extractor=pdf_extractor,
    chunker=chunker,
    embedding_service=embedding_service,
    pinecone_service=pinecone_service
)

# Process with different chunking strategy
result = parser.process_contract("contract.pdf", chunking_strategy="sentences")
```

### Single File Processing

```python
# Process one contract
result = parser.process_contract("contract.pdf", chunking_strategy="sentences")
```

### Batch Processing

```python
# Process multiple specific contracts
pdf_paths = ["contract1.pdf", "contract2.pdf", "contract3.pdf"]
results = parser.batch_process_contracts(pdf_paths, chunking_strategy="sentences")

# Process all PDFs in a directory
from main import batch_process_contracts
results = batch_process_contracts("contracts_folder", chunking_strategy="sentences")
```

### Interactive Search

```python
# Run interactive search session
parser.interactive_search()
```

## Processing Modes

The system supports three processing modes:

### 1. Single File Mode
```python
PROCESSING_MODE = "single"
single_pdf_path = "test_pdfs/loan_contract.pdf"
```

### 2. Batch Files Mode
```python
PROCESSING_MODE = "batch"
batch_pdf_paths = [
    "test_pdfs/loan_contract.pdf",
    "test_pdfs/trust_contract.pdf", 
    "test_pdfs/credit_contract.pdf"
]
```

### 3. Directory Mode
```python
PROCESSING_MODE = "directory"
pdf_directory = "test_pdfs"  # Processes all PDFs in folder
```

## 🔍 Search Examples

```python
# Search for termination clauses
results = parser.search_contract("When can I terminate the contract?")

# Search for payment terms
results = parser.search_contract("What are the payment terms and conditions?")

# Search for liability clauses
results = parser.search_contract("What are the liability limitations?")

# Search with custom parameters
results = parser.search_contract(
    query="confidentiality requirements",
    top_k=5,
    filter_dict={"heading": {"$contains": "confidentiality"}}
)
```

## Chunking Strategies

### 1. Clauses (Default)
Splits text based on numbered clause patterns:

1. TERMINATION
This agreement may be terminated...

2. PAYMENT TERMS
Payment shall be made...


### 2. Sentences
Splits text into sentence-based chunks with size limits.

### 3. Paragraphs
Splits text based on paragraph boundaries.

## 🏛️ Module Structure

### `config.py`
- Centralized configuration management
- Environment variable support
- Default settings

### `pdf_extractor.py`
- PDF text extraction using PyPDF2
- Page-by-page processing
- Error handling for corrupted PDFs

### `text_chunker.py`
- Multiple chunking strategies
- Configurable patterns
- Chunk statistics and metadata
- Automatic fallback to sentence chunking for large documents

### `embedding_service.py`
- SentenceTransformer integration
- Batch encoding for efficiency
- Similarity computation utilities

### `pinecone_service.py`
- Vector database operations
- Batch upserting
- Search and filtering capabilities

### `contract_parser.py`
- Main orchestrator class
- Pipeline coordination
- High-level API


## Testing

```python
# Validate PDF before processing
validation = parser.validate_pdf("contract.pdf")
if validation["valid"]:
    print(f"PDF is valid: {validation['page_count']} pages")
else:
    print(f"PDF validation failed: {validation['error']}")

# Get system statistics
stats = parser.get_contract_statistics()
print(f"Index contains {stats['index_statistics']['total_vector_count']} vectors")
```

## Quick Start Examples

### Single Contract
```bash
# Edit main.py: PROCESSING_MODE = "single"
python main.py
```

### Multiple Contracts
```bash
# Edit main.py: PROCESSING_MODE = "batch"
python main.py
```

### All PDFs in Directory
```bash
# Edit main.py: PROCESSING_MODE = "directory"
python main.py
```

### Direct Batch Processing
```bash
python -c "from main import batch_process_contracts; batch_process_contracts('test_pdfs', 'sentences')"
```