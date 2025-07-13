from PyPDF2 import PdfReader
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Handles extraction of text from PDF files."""
    
    def __init__(self):
        self.reader: Optional[PdfReader] = None
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a single string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF reading fails
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            self.reader = PdfReader(pdf_path)
            
            if not self.reader.pages:
                raise ValueError("PDF appears to be empty")
            
            text_parts = []
            for i, page in enumerate(self.reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(page_text)
                logger.debug(f"Extracted text from page {i+1}")
            
            full_text = "\n".join(text_parts)
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_path}")
            raise
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def get_page_count(self) -> int:
        """Get the number of pages in the loaded PDF."""
        if self.reader is None:
            raise ValueError("No PDF loaded. Call extract_text() first.")
        return len(self.reader.pages)
    
    def extract_text_from_page(self, page_number: int) -> str:
        """
        Extract text from a specific page.
        
        Args:
            page_number: 0-indexed page number
            
        Returns:
            Text from the specified page
        """
        if self.reader is None:
            raise ValueError("No PDF loaded. Call extract_text() first.")
        
        if page_number >= len(self.reader.pages):
            raise ValueError(f"Page {page_number} does not exist. PDF has {len(self.reader.pages)} pages.")
        
        return self.reader.pages[page_number].extract_text() 