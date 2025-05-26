from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.parser import extract_fields, extract_text_docx, extract_text_pdf, matcher, nlp
from app.utils.llm_extractor import enrich_llm_response

def normalize_skills(skills: list[str]) -> set[str]:
    return {s.lower().replace("-", " ").replace("_", " ").strip() for s in skills}

router = APIRouter(tags=["Match"])

@router.post("/upload")
async def unified_resume_match(
        resume_file: UploadFile = File(...),
        jd_file: Optional[UploadFile] = File(None),
        jd_text: Optional[str] = Form(None)
    ):
    
    # Parse resume
    if not resume_file.filename.endswith(('.docx', '.pdf')):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX resumes are supported.")
    
    resume_bytes = await resume_file.read()
    resume_text = (
        extract_text_pdf(resume_bytes) if resume_file.filename.endswith('.pdf')
        else extract_text_docx(resume_bytes)
    )

    if not resume_text:
        raise HTTPException(status_code=500, detail="Failed to extract text from given resume.")
    
    resume_fields = extract_fields(resume_text)
    resume_fields= enrich_llm_response(resume_text, resume_fields)
    resume_skills= normalize_skills(resume_fields.get("skills",[]))
    

    

    # Parse JD
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
            raise HTTPException(status_code=400, detail="Invalid JD file type.")
    else:
        jd_content = jd_text

    if not jd_content:
        raise HTTPException(status_code=400, detail="JD text is missing or unreadable.")
    
    jd_doc = nlp(jd_content)
    jd_skills_raw = [jd_doc[start:end].text for _, start, end in matcher(jd_doc)]

    # Normalize both sides
    
    jd_skills = normalize_skills(jd_skills_raw)

    # Skill matching
    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    percent = round((len(matched) / len(jd_skills)) * 100, 2) if jd_skills else 0.0

    return {
        "resume_fields": resume_fields,
        "jd_skills": sorted(jd_skills),
        "resume_skills": sorted(resume_skills),
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": percent
    }
