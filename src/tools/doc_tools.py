from docling.document_converter import DocumentConverter
from typing import List, Dict, Optional
import os

class DocAnalystTools:
    """
    Forensic tools for analyzing PDF reports.
    Uses Docling for structured extraction and provides RAG-lite querying.
    """

    def __init__(self):
        self.converter = DocumentConverter()

    def ingest_pdf(self, pdf_path: str) -> str:
        """Parses a PDF and returns the full text content. Includes fallback discovery."""
        actual_path = pdf_path
        if not os.path.exists(pdf_path):
            print(f"Target PDF {pdf_path} not found. Searching for fallbacks in root...")
            # Fallback search
            potential_pdfs = [f for f in os.listdir(".") if f.endswith(".pdf")]
            if potential_pdfs:
                actual_path = potential_pdfs[0]
                print(f"Found fallback PDF: {actual_path}")
            else:
                raise FileNotFoundError(f"No PDF found at {pdf_path} and no fallbacks available.")
        
        result = self.converter.convert(actual_path)
        return result.document.export_to_markdown()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
        """Simple character-based chunking for RAG-lite."""
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    @staticmethod
    def query_context(text: str, keywords: List[str]) -> str:
        """
        Extends a 'RAG-lite' approach by extracting paragraphs containing keywords.
        """
        paragraphs = text.split("\n\n")
        relevant_context = []
        for para in paragraphs:
            if any(key.lower() in para.lower() for key in keywords):
                relevant_context.append(para)
        
        return "\n\n".join(relevant_context[:5]) # Return up to 5 relevant paragraphs

if __name__ == "__main__":
    # Test stub
    pass
