import fitz
import spacy
from spacy.matcher import PhraseMatcher
import docx
from io import BytesIO
from typing import Optional
import logging
import re
import fitz.fitz

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
logger = logging.getLogger(__name__)

SKILL_KEYWORDS = [
    "python", "java", "c++", "sql", "postgresql", "mongodb", "ms sql", "ms sql server",
    "redis", "graphql", "big query", "looker", "selenium", "numpy", "pandas",
    "tensorflow", "pytorch", "flask", "pyspark", "airflow", "github", "aws", "ec2",
    "lambda", "glue", "redshift", "docker", "kubernetes", "git", "hadoop",
    "team work", "adaptability", "leadership experience", "problem-solving", "agile",
    "cross functional", "detail oriented", "quality assurance", "strong communication",
    "drafting", "research", "problem solving"
]

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
skill_patterns = [nlp.make_doc(skill) for skill in SKILL_KEYWORDS]
matcher.add("SKILLS", skill_patterns)


def clean_skill(text: str) -> str:
    return (
        text.lower()
        .replace("\n", " ")
        .replace("•", "")
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )

# Hybrid skill extractor
def extract_skills_hybrid(text: str) -> list[str]:
    doc = nlp(text)

    # PhraseMatcher skills
    phrase_matches = matcher(doc)
    phrase_skills = {doc[start:end].text for _, start, end in phrase_matches}

    # NER fallback
    ner_skills = {
        ent.text for ent in doc.ents
        if ent.label_ in {"ORG", "PRODUCT", "WORK_OF_ART"} and len(ent.text.strip()) > 1
    }

    # Capitalized noun chunks
    chunk_skills = {
        chunk.text for chunk in doc.noun_chunks
        if chunk.text[0].isupper() and len(chunk.text.strip().split()) <= 3
    }

    all_skills = phrase_skills | ner_skills | chunk_skills

    # Clean + filter bad skills
    cleaned_skills = {
        clean_skill(skill)
        for skill in all_skills
        if not re.search(r"(@|\.com|linkedin\.com|http)", skill.lower())
        and len(skill) > 1
    }

    return sorted(cleaned_skills)


# Extract key fields from resume text
def extract_fields(text: str) -> dict:
    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    doc = nlp(text)

    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "")
    email_match = re.search(r"[a-zA-Z0-9_.=-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = email_match.group() if email_match else ""
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", text)
    phone_number = phone_match.group() if phone_match else ""
    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com\/[a-zA-Z0-9\-_/]+", text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else ""
    github_match = re.search(r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9-_]+", text)
    github = github_match.group() if github_match else ""
    address = next((ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC"}), "")

    skills = extract_skills_hybrid(text)

    return {
        "name": name or "Not Available",
        "email": email or "Not Available",
        "phone": phone_number or "Not Available",
        "linkedin": linkedin or "Not Available",
        "github": github or "Not Available",
        "skills": skills or ["Not Available"],
        "address": address or "Not Available"
    }


# PDF text extractor
def extract_text_pdf(file_bytes: bytes) -> Optional[str]:
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            page_texts = [page.get_text() for page in doc]
            return "".join(page_texts)
    except fitz.fitz.FileDataError as fe:
        logger.error(f"Error reading PDF file: {fe}")
        return None
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None


# DOCX text extractor
def extract_text_docx(file_bytes: bytes) -> Optional[str]:
    try:
        doc = docx.Document(BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}", exc_info=True)
        return None
