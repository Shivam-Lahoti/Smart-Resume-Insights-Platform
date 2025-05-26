from fastapi import FastAPI
from app.api.v1 import resume,job,match

app = FastAPI(title="Smart Resume Insights Platfrom")

#Resume Routes
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])

#job Routes
app.include_router(job.router, prefix="/api/v1/job", tags=["Job"])

#match Routes
app.include_router(match.router, prefix="/api/v1/match", tags=["Match"])



@app.get("/")
def root():
    return{"messagae":"Smart Resume Insights Platfrom is up and running"}
