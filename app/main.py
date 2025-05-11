from fastapi import FastAPI
from app.api.v1 import resume

app = FastAPI(title="Smart Resume Insights Platfrom")

#Resume Routes
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])

@app.get("/")
def root():
    return{"messagae":"Smart Resume Insights Platfrom is up and running"}
