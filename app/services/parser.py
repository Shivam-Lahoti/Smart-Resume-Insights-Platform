import fitz
import docx
from io import BytesIO
from typing import Optional
import logging

import fitz.fitz


logger = logging.getLogger(__name__)


#This extract text from pdf
def extract_text_pdf(file_bytes: bytes) -> Optional[str]:
    """Extracts Text from PDF File"""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            page_texts= [page.get_text() for page in doc]
            return "".join(page_texts)
    except fitz.fitz.FileDataError as fe:
        logger.error(f"Error reading PDF file: {fe}")
        return None
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None
    
#This extracts text from docs
def extract_text_docx(file_bytes: bytes) -> Optional[str]:
    """Extracts Text from DOCX File"""
    try:
        doc = docx.Document(BytesIO(file_bytes))
        text= "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}", exc_info=True)
        return None
    