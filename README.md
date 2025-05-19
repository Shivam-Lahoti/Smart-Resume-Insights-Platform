# 🧠 Smart Resume Insights Platform (SRIP)

A FastAPI-powered backend service that allows users to upload resume files (PDF/DOCX), extract their text content and structured fields, and preview it for further AI-based analysis. SRIP is designed as the foundation for a full-stack platform that provides career insights, resume optimization, and job matching capabilities.

---

## 🚀 Features

- Upload support for 1 or 2 resume files at a time
- Parses PDF and DOCX using PyMuPDF and python-docx
- Extracts structured fields: name, email, phone, LinkedIn, GitHub, address, skills
- Upload JD as file or raw text and extract JD skills
- Match resume skills against job description (JD) skills
- Logs errors and exceptions for easy debugging
- Extensible design for LLM-based analysis, summarization, and recommendation

---

## 📁 Project Structure

```
SRIP/
├── app/
│   ├── api/v1/resume.py         # Resume upload & parsing logic
│   ├── api/v1/job.py            # JD upload & skill matching endpoints
│   ├── services/parser.py       # Extraction logic (PDF, DOCX, skills, NER)
│   └── main.py                  # FastAPI app entry point
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── __init__.py
```

---

## 📄 Requirements

- Python 3.10+
- pip (Python package installer)

### Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/smart-resume-insights.git
cd smart-resume-insights
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv env
# Windows
env\Scripts\activate
# macOS/Linux
source env/bin/activate
```

### 3. Run the API Server

```bash
# Set PYTHONPATH
$env:PYTHONPATH="SRIP"       # On Windows
export PYTHONPATH=SRIP       # On Mac/Linux

uvicorn app.main:app --reload
```

---

## 🌐 API Usage (via Swagger)

Open in browser:  
👉 http://localhost:8000/docs

---

## 📤 Resume Upload

```
POST /api/v1/resume/upload
```

### Accepts:
- 1 or 2 `.pdf` or `.docx` files
- Extracts text, name, email, phone, address, skills

### Response:
```json
[
  {
    "filename": "resume.pdf",
    "status": "processed",
    "preview": "Shivam Lahoti\n95, Boylston St, Brookline, MA...",
    "extracted_fields": {
      "name": "Shivam Lahoti",
      "email": "shivam.2199@gmail.com",
      "skills": ["python", "aws", "docker", "kubernetes", ...]
    }
  }
]
```

---

## 📋 Job Description Upload

```
POST /api/v1/job/upload-jd
```

### Accepts:
- JD as `.pdf`, `.docx`, `.txt`, or raw pasted text

### Response:
```json
{
  "jd_text": "We are hiring a backend engineer...",
  "extracted_jd_skills": ["python", "aws", "docker", "kubernetes", ...],
  "match_count": 10
}
```

---

## 🎯 Resume–JD Skill Match

```
POST /api/v1/job/match
```

### Sample Request:
```json
{
  "resume_skills": ["python", "docker", "aws", "git"],
  "jd_skills": ["python", "docker", "aws", "postgresql", "kubernetes"]
}
```

### Response:
```json
{
  "matched_skills": ["aws", "docker", "python"],
  "missing_skills": ["kubernetes", "postgresql"],
  "match_percent": 60.0,
  "resume_skill_count": 4,
  "jd_skill_count": 5
}
```

---

## 🚪 Error Handling

| Scenario                       | Response Code | Message                                      |
|-------------------------------|---------------|----------------------------------------------|
| More than 2 files uploaded     | 400           | "You can upload up to 2 files at a time."    |
| Invalid file type              | 400           | "Only PDF or DOCX files are allowed."        |
| No JD text provided            | 400           | "JD text is empty or could not be read."     |
| File parsing failure           | 500           | "An unexpected error occurred during parsing."|

---

## 🧩 Future Roadmap

- ✅ Resume parsing + structured field extraction
- ✅ JD upload and skill extraction
- ✅ Resume–JD skill match scoring
- ⏳ Resume summarizer (LLM)
- ⏳ RAG-based job recommendation engine
- ⏳ MongoDB/PostgreSQL integration
- ⏳ Frontend (Streamlit / React)
- ⏳ Docker containerization
- ⏳ Deployment on Render / AWS

---

## 👨‍💻 Author

**Shivam Lahoti**  
Graduate Student, Northeastern University  
📧 shivam.2199@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/shivam-lahoti-2811501b1/)

---

## 📃 License

MIT License – use freely with attribution.