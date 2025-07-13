# Contract Parser - Modular PDF Analysis System

A clean, modular system for extracting text from contract PDFs, chunking into clauses, generating embeddings, and enabling semantic search using Pinecone.

## 🏗️ Architecture

The system is built with a modular, clean architecture:

```
pdf-parser/
├── config.py              # Configuration management
├── pdf_extractor.py       # PDF text extraction
├── text_chunker.py        # Text chunking strategies
├── embedding_service.py   # Embedding generation
├── pinecone_service.py    # Vector database operations
├── contract_parser.py     # Main orchestrator class
├── main.py               # Demo and usage examples
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 📋 Requirements

- Python 3.8+
- Pinecone account and API key
- Internet connection (for downloading embedding models)

## 🛠️ Installation

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

## 📖 Usage

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

### Batch Processing

```python
# Process multiple contracts
pdf_paths = ["contract1.pdf", "contract2.pdf", "contract3.pdf"]
results = parser.batch_process_contracts(pdf_paths, chunking_strategy="clauses")
```

### Interactive Search

```python
# Run interactive search session
parser.interactive_search()
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

## 📊 Chunking Strategies

### 1. Clauses (Default)
Splits text based on numbered clause patterns:
```
1. TERMINATION
   This agreement may be terminated...

2. PAYMENT TERMS
   Payment shall be made...
```

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

## 🔧 Customization

### Custom Chunking Pattern

```python
from text_chunker import TextChunker

# Custom pattern for your document format
custom_pattern = r"(?:^|\n)(Article\s+\d+\.\s+[A-Z][^\n]+)"
chunker = TextChunker(pattern=custom_pattern)
```

### Custom Embedding Model

```python
from embedding_service import EmbeddingService

# Use a different model
embedding_service = EmbeddingService(model_name="all-mpnet-base-v2")
```

### Custom Pinecone Configuration

```python
from pinecone_service import PineconeService

# Custom Pinecone setup
pinecone_service = PineconeService(
    api_key="your-key",
    environment="your-env",
    index_name="custom-index"
)
```

## 📝 Logging

The system provides comprehensive logging:

```python
import logging

# Set log level
logging.basicConfig(level=logging.INFO)

# Logs are written to both console and file
# Check contract_parser.log for detailed logs
```

## 🧪 Testing

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

## 🚨 Error Handling

The system handles various error scenarios:

- **Invalid PDF files**: Validation before processing
- **Network issues**: Retry logic for Pinecone operations
- **Empty documents**: Graceful handling of empty PDFs
- **API limits**: Batch processing to avoid rate limits

## 🔒 Security Notes

- Store API keys in environment variables
- Never commit API keys to version control
- Use appropriate Pinecone environment settings
- Consider data privacy when processing sensitive contracts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Pinecone API Key Error**
   - Verify your API key is correct
   - Check your Pinecone environment setting

2. **PDF Extraction Fails**
   - Ensure the PDF is not password-protected
   - Check if the PDF contains extractable text

3. **Embedding Model Download Fails**
   - Check your internet connection
   - Verify you have sufficient disk space

4. **Memory Issues with Large PDFs**
   - Use sentence or paragraph chunking instead of clauses
   - Process PDFs in smaller batches

### Getting Help

- Check the logs in `contract_parser.log`
- Verify your configuration in `config.py`
- Ensure all dependencies are installed correctly 