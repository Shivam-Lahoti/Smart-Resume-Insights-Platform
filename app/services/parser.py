import fitz
import docx
from io import BytesIO
from typing import Optional
import logging
import re
import fitz.fitz


logger = logging.getLogger(__name__)

SKILL_KEYWORDS= ["python", "java", "c++", "sql", "aws", "docker", "kubernetes",
    "git", "react", "node", "tensorflow", "pytorch", "nlp", "fastapi",
    "data analysis", "machine learning", "communication", "leadership"]

#Extract Fields
def extract_fields(text: str) -> dict:
    lines= text.splitlines()
    non_empty_lines= [line.strip() for line in lines if line.strip()]

    #Name
    name= non_empty_lines[0] if non_empty_lines else ""

    #email
    email_match= re.search(r"[a-zA-Z0-9_.=-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email= email_match.group() if email_match else ""

    #Phone
    Phone_match=re.search(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", text)
    Phone= Phone_match.group() if Phone_match else ""

    #LinkedIn
    linkedin_match= re.search(r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9-_]+", text)
    linkedin= linkedin_match.group() if linkedin_match else ""

    #Github
    github_match= re.search(r"https?://)?(www\.)?github\.com/[a-zA-Z0-9-_]+",text)
    github= github_match.group() if github_match else ""

    #Addres
    address= ""
    for line in non_empty_lines[1:4]:
        if any(word in line.lower() for word in ["street", "st", "road", "rd", "lane", "blvd", "ave", "city", "zip", "state"]):
            address= line
            break

    #Skills
    # Skills: exact matches from SKILL_KEYWORDS
    found_skills = set()
    for skill in SKILL_KEYWORDS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            found_skills.add(skill.lower())

        
        return {
        "name": name if name else "Not Available",
        "email": email if email else "Not Available",
        "phone": Phone if Phone else "Not Available",
        "linkedin": linkedin if linkedin else "Not Available",
        "github": github if github else "Not Available",
        "skills": list(found_skills) if found_skills else ["Not Available"],
        "address": address if address else "Not Available"
    }








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
    