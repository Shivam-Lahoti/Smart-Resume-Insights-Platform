import fitz
import docx
from io import BytesIO
from typing import Optional
import logging
import re
import fitz.fitz


logger = logging.getLogger(__name__)

SKILL_KEYWORDS = [
    "python", "java", "c++", "sql", "postgresql", "mongodb", "ms sql", "ms sql server",
    "redis", "graphql", "big query", "looker", "selenium", "numpy", "pandas",
    "tensorflow", "pytorch", "flask", "pyspark", "airflow", "github", "aws", "ec2",
    "lambda", "glue", "redshift", "docker", "kubernetes", "git", "hadoop",
    "team work", "adaptability", "leadership experience", "problem-solving", "agile",
    "cross functional", "detail oriented"
]

#Extract Fields
def extract_fields(text: str) -> dict:
    lines= text.splitlines()
    non_empty_lines= [line.strip() for line in lines if line.strip()]
    normalized_text= text.lower()
    print(normalized_text)

    #Name
    name= non_empty_lines[0] if non_empty_lines else ""

    #email
    email_match= re.search(r"[a-zA-Z0-9_.=-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email= email_match.group() if email_match else ""

    #Phone
    Phone_match=re.search(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", text)
    Phone= Phone_match.group() if Phone_match else ""

    #LinkedIn
    linkedin_match= re.search(r"(https?://)?(www\.)?linkedin\.com\/[a-zA-Z0-9\-_/]+", text, re.IGNORECASE)
    linkedin= linkedin_match.group() if linkedin_match else ""

    #Github
    github_match= re.search(r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9-_]+",text)
    github= github_match.group() if github_match else ""

    #Addres
    address= ""
    for line in non_empty_lines[0:5]:
        line_lower = line.lower()
        location_keywords=["street", "st", "road", "rd", "lane", "blvd", "ave", "city", "zip", "state", "massachusetts", "india", "usa"]
        contact_keywords= ["@", "linkedin.com", "github.com", "http", "www.", ".com", "gmail"]
        if (
            any(word in line_lower for word in location_keywords)
                and not any(kw in line_lower for kw in contact_keywords )
            ):
                address = line.strip()
                break
    #Skills
    # Skills: exact matches from SKILL_KEYWORDS
    found_skills = set()
    for skill in SKILL_KEYWORDS:
        if skill.lower() in normalized_text:
            print(f"Skill Matched: {skill},")
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
    