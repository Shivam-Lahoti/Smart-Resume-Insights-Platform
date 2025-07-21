from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str]

class ResumeCreate(BaseModel):
    file_name: str
    raw_text: str
    extracted_skill: List[str]

class  JobDescriptionCreate(BaseModel):
    file_name: str
    jd_text: str
    jd_skills: List[str]


class MatchResultCreate(BaseModel):
    resume_id: int
    jd_id: int
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: str
    llm_recommendation: Optional[str]