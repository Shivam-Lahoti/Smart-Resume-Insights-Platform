from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.parser import extract_text_pdf, extract_text_docx, extract_fields, matcher, nlp
from app.utils.llm_extractor import enrich_llm_response, enrich_jd_skills_with_llm, generate_llm_recommendation


router = APIRouter(tags=["Match"])

def normalize_skills(skills: list[str]) -> set[str]:
    return {s.lower().replace("-", " ").replace("_", " ").strip() for s in skills}

@router.post("/upload")
async def unified_resume_match(
    resume_file: UploadFile = File(...),
    jd_file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None)
):
    if not resume_file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX resumes are supported.")

    # Extract resume text
    resume_bytes = await resume_file.read()
    resume_text = (
        extract_text_pdf(resume_bytes) if resume_file.filename.endswith('.pdf')
        else extract_text_docx(resume_bytes)
    )
    if not resume_text or len(resume_text.strip()) < 50:
        raise HTTPException(status_code=500, detail="Failed to extract meaningful content from resume.")

    # Extract and enrich resume fields
    extracted_fields = extract_fields(resume_text)
    enriched_resume = enrich_llm_response(resume_text, extracted_fields)

    name = enriched_resume.get("name", "Not Available")
    email = enriched_resume.get("email", "Not Available")
    phone = enriched_resume.get("phone", "Not Available")
    linkedin = enriched_resume.get("linkedin", "Not Available")
    github = enriched_resume.get("github", "Not Available")
    address = enriched_resume.get("address", "Not Available")

    resume_keywords = normalize_skills(enriched_resume.get("skills", []))

    # Extract JD text
    jd_content = ""
    if jd_file:
        jd_bytes = await jd_file.read()
        if jd_file.filename.endswith('.pdf'):
            jd_content = extract_text_pdf(jd_bytes)
        elif jd_file.filename.endswith('.docx'):
            jd_content = extract_text_docx(jd_bytes)
        elif jd_file.filename.endswith('.txt'):
            jd_content = jd_bytes.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported JD file type.")
    elif jd_text:
        jd_content = jd_text

    if not jd_content or len(jd_content.strip()) < 50:
        raise HTTPException(status_code=400, detail="JD text is missing or too short.")

    # Extract and enrich JD skills
    jd_doc = nlp(jd_content)
    jd_skills_raw = [jd_doc[start:end].text for _, start, end in matcher(jd_doc)]
    jd_skills_raw = list(set(jd_skills_raw))

    enriched_jd_skills = enrich_jd_skills_with_llm(jd_content, jd_skills_raw)
    jd_keywords = normalize_skills(enriched_jd_skills)

    # Keyword comparison
    missing_keywords = sorted(jd_keywords - resume_keywords)
    match_percentage = round(((len(jd_keywords) - len(missing_keywords)) / len(jd_keywords)) * 100, 2) if jd_keywords else 0.0

    # LLM recommendation
    recommendation = generate_llm_recommendation(jd_keywords, resume_keywords, missing_keywords)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "address": address,
        "resume_keywords": sorted(list(resume_keywords)),
        "jd_keywords": sorted(list(jd_keywords)),
        "missing_keywords": missing_keywords,
        "match_summary": {
            "total_jd_keywords": len(jd_keywords),
            "missing_in_resume": len(missing_keywords),
            "match_percentage": match_percentage
        },
        "llm_recommendation": recommendation
    }





