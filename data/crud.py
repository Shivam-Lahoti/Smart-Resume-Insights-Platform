from sqlalchemy.orm import Session
from . import models, schemas

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_resume(db: Session, resume: schemas.ResumeCreate, user_id: int):
    db_resume = models.Resume(user_id=user_id, **resume.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def create_jd(db: Session, jd: schemas.JobDescriptionCreate, user_id: int):
    db_jd = models.JobDescription(user_id=user_id, **jd.dict())
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd
