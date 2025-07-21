from sqlalchemy import Boolean,Column, Integer, String, ForeignKey, JSON, Text, DateTime, func
from sqlalchemy.orm import relationship
from data.db import Base

class User(Base):
    __tablename__= "users"
    id= Column(Integer, primary_key=True, index=True)
    email= Column(String, unique= True, index= True, nullable= False)
    is_active= Column(Boolean, default= True)
    hashed_password= Column(String, nullable= False)
    full_name= Column(String, nullable= True)
    created_at= Column(DateTime(timezone= True), server_default= func.now())

    resumes= relationship("Resume", back_populates="user")
    jobs= relationship("JobDescription", back_populates="user")


class Resume(Base):
    __tablename__= "resumes"
    id= Column(Integer, primary_key=True, index=True)
    user_id= Column(Integer, ForeignKey("users.id"))
    file_name= Column(String)
    raw_text= Column(Text)
    extracted_skill= Column(JSON)
    created_at= Column(DateTime(timezone= True), server_default= func.now())

    user= relationship("User", back_populates="resumes")

class JobDescription(Base):
    __tablename__= "job_descriptions"
    id= Column(Integer, primary_key=True, index=True)
    user_id= Column(Integer, ForeignKey("users.id"))
    jd_text= Column(Text)
    jd_skills= Column(JSON)
    created_at= Column(DateTime(timezone=True), server_default=func.now())

    user= relationship("User", back_populates="jobs")

class MatchResults(Base):
    __tablename__= "match_results"
    id= Column(Integer, primary_key=True, index=True)
    user_id= Column(Integer, ForeignKey("users.id"))
    resume_id= Column(Integer, ForeignKey("resumes.id"))
    jd_id= Column(Integer, ForeignKey("job_descriptions.id"))

    matched_skills= Column(JSON)
    missing_skills= Column(JSON)
    match_percentage= Column(Integer)
    llm_recommendation= Column(Text)
    created_at= Column(DateTime(timezone=True), server_default=func.now())



    
