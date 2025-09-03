import os
import tempfile
import docx
import PyPDF2
from typing import Optional

class DocumentProcessor:
    def __init__(self):
        """Initialize document processor"""
        self.supported_extensions = ['txt', 'pdf', 'docx']
    
    def extract_text(self, file_path: str, file_extension: str) -> str:
        """
        Extract text from a document file
        
        Args:
            file_path: Path to the file
            file_extension: File extension (txt, pdf, docx)
            
        Returns:
            Extracted text content
        """
        try:
            if file_extension == "pdf":
                with open(file_path, "rb") as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return text
            elif file_extension == "docx":
                doc = docx.Document(file_path)
                return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            elif file_extension == "txt":
                with open(file_path, "r", encoding="utf-8") as file:
                    return file.read()
            else:
                return "Unsupported file type"
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def is_supported(self, filename: str) -> bool:
        """
        Check if a file is supported based on its extension
        
        Args:
            filename: The name of the file
            
        Returns:
            True if the file type is supported, False otherwise
        """
        file_extension = filename.split('.')[-1].lower()
        return file_extension in self.supported_extensions
    
    def get_extension(self, filename: str) -> str:
        """
        Get the file extension from a filename
        
        Args:
            filename: The name of the file
            
        Returns:
            The file extension
        """
        return filename.split('.')[-1].lower()