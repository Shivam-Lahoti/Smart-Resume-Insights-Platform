from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.parser import extract_fields, extract_text_docx, extract_text_pdf, matcher, nlp
from app.utils.llm_extractor import enrich_llm_response, enrich_jd_skills_with_llm
from sentence_transformers import SentenceTransformer, util
import numpy as np

model= SentenceTransformer('all-MiniLM-L6-v2')

router = APIRouter(tags=["Match"])

def normalize_skills(skills: list[str]) -> set[str]:
    return {s.lower().replace("-", " ").replace("_", " ").strip() for s in skills}

def semantic_match(resume_skills: list[str], jd_skills: list[str], threshold: float= 0.6):
    resume_emmbeddings= model.encode(list(resume_skills), convert_to_tensor= True)
    jd_embeddings= model.encode(list(jd_skills), convert_to_tensor=True)

    matched= []
    for i, jd_skill in enumerate(jd_skills):
        similarity_scores= util.cos_sim(jd_embeddings[i], resume_emmbeddings)[0]
        best_score_idx= similarity_scores.argmax().item()
        best_score= similarity_scores[best_score_idx]
        if best_score>= threshold:
            matched.append(jd_skill)

    missing= [skill for skill in jd_skills if skill not in matched]
    return matched, missing

@router.post("/upload")
async def unified_resume_match(
    resume_file: UploadFile = File(...),
    jd_file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None)
):
    if not resume_file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX resumes are supported.")

    resume_bytes = await resume_file.read()
    resume_text = (
        extract_text_pdf(resume_bytes) if resume_file.filename.endswith('.pdf')
        else extract_text_docx(resume_bytes)
    )

    if not resume_text:
        raise HTTPException(status_code=500, detail="Failed to extract text from resume.")

    extracted_fields = extract_fields(resume_text)
    enriched_resume = enrich_llm_response(resume_text, extracted_fields)

    name = enriched_resume.get("name", "Not Available")
    email = enriched_resume.get("email", "Not Available")
    phone = enriched_resume.get("phone", "Not Available")
    linkedin = enriched_resume.get("linkedin", "Not Available")
    github = enriched_resume.get("github", "Not Available")
    address = enriched_resume.get("address", "Not Available")

    llm_resume_skills = normalize_skills(enriched_resume.get("skills", []))

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

    if not jd_content:
        raise HTTPException(status_code=400, detail="JD text is missing or unreadable.")

    jd_doc = nlp(jd_content)
    jd_skills_raw = [jd_doc[start:end].text for _, start, end in matcher(jd_doc)]
    jd_skills_raw = list(set(jd_skills_raw))

    enriched_jd_skills = enrich_jd_skills_with_llm(jd_content, jd_skills_raw)
    llm_jd_skills = normalize_skills(enriched_jd_skills)

    matched_skills, missing_skills = semantic_match(llm_resume_skills, llm_jd_skills)
    match_percentage = round((len(matched_skills) / len(llm_jd_skills)) * 100, 2) if llm_jd_skills else 0.0

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "address": address,
        "llm_resume_skills": sorted(set(llm_resume_skills)),
        "llm_jd_skills": sorted(set(llm_jd_skills)),
        "matched_skills": sorted(set(matched_skills)),
        "missing_skills": sorted(set(missing_skills)),
        "match_percentage": match_percentage
    }
