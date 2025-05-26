from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
from app.services.parser import extract_fields,extract_text_docx,extract_text_pdf, matcher, SKILL_KEYWORDS, nlp
from pydantic import BaseModel
from typing import List,Set

def normalize_skills(skills: list[str]) -> set[str]:
    return {s.lower().replace("-", " ").replace("_", " ").strip() for s in skills}



router = APIRouter()

@router.post("/upload-jd")
async def upload_jd(file:Optional[UploadFile] = File(None), text:Optional[str] = Form(None)):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide .pdf,.docx,.txt file or raw text")
    
    jd_text= ""

    if file:
        try:
            contents= await file.read()
            if file.filename.endswith(".pdf"):
                jd_text= extract_text_pdf(contents)
                if jd_text is None: # Check if extraction failed
                    raise ValueError("Failed to extract text from PDF.")
            elif file.filename.endswith(".docx"):
                jd_text= extract_text_docx(contents)
                if jd_text is None: # Check if extraction failed
                    raise ValueError("Failed to extract text from DOCX.")
            elif file.filename.endswith(".txt"):
                jd_text= contents.decode("utf-8")
            else:
                raise HTTPException(status_code=400, detail="Invalid file")
        except Exception as e:
            # Log the exception e for debugging
            raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
    elif text: # Process text only if no file was provided, or if file processing is separate
        jd_text = text
    
    # If jd_text is still empty after attempting to process file (if provided) or text (if provided)
    if not jd_text:
 
        raise HTTPException(status_code=400, detail="JD text is empty or could not be read.")
        
    # Perform skill extraction on the obtained jd_text
    try:
        doc = nlp(jd_text)
        matches = matcher(doc)
        jd_skills_set = set([doc[start:end].text.lower() for _, start, end in matches]) # Use .text for spaCy 2.x/3.x spans
    except Exception as e:
        # Log the exception e for debugging
        raise HTTPException(status_code=500, detail=f"Skill extraction failed: {str(e)}")

    return {
        "jd_text": jd_text[:1000] + "..." if len(jd_text) > 1000 else jd_text,
        "extracted_jd_skills": sorted(list(jd_skills_set)) if jd_skills_set else ["Not Found"],
        "match_count": len(jd_skills_set)
    }


class MatchRequest(BaseModel):
    resume_skills: List[str]
    jd_skills: List[str]

@router.post("/match")
async def resume_match_skills(data: MatchRequest):
    resume_set = normalize_skills(data.resume_skills)
    jd_set = normalize_skills(data.jd_skills)

    
    matched_skills= sorted(resume_set.intersection(jd_set))
    missing_skills= sorted(jd_set-resume_set)

    total_required= len(jd_set)
    match_percent= round((len(matched_skills)/total_required)*100,2) if total_required else 0.0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percent": match_percent,
        "resume_skill_count": len(resume_set),
        "jd_skill_count": total_required
    }


