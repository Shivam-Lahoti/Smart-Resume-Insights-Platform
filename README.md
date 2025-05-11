# 🧠 Smart Resume Insights Platform (SRIP)

A FastAPI-powered backend service that allows users to upload resume files (PDF/DOCX), extract their text content, and preview it for further AI-based analysis. SRIP is designed to serve as the foundation for a full-stack platform that provides career insights, resume optimization, and job matching capabilities.

---

## 🚀 Features

* Upload support for 1 or 2 resume files at a time
* Parses PDF and DOCX files using PyMuPDF and python-docx
* Extracts and previews up to 1000 characters from resume content
* Validates file types and limits uploads to only PDF or DOCX
* Logs errors and exceptions for debugging
* Extensible architecture for future AI/NLP capabilities

---

## 📁 Project Structure

```
SRIP/
├── app/
│   ├── api/v1/resume.py         # Upload endpoint and logic
│   ├── services/parser.py       # Resume parsing functions (PDF/DOCX)
│   └── main.py                  # FastAPI entry point
├── tests/                       # Placeholder for unit tests
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── __init__.py                  # Marks SRIP as a Python package
```

---

## 📄 Requirements

* Python 3.10 or newer
* pip (Python package installer)

### Python Libraries:

Install via:

```bash
pip install -r requirements.txt
```

Libraries used:

* fastapi
* uvicorn
* python-docx
* PyMuPDF
* pydantic
* python-multipart

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/srip.git
cd srip
```

### 2. Create a Virtual Environment

```bash
python -m venv env
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
# If you're in SRIP directory:
$env:PYTHONPATH="SRIP"       # On Windows
export PYTHONPATH=SRIP       # On Mac/Linux

uvicorn app.main:app --reload
```

---

## 🌐 API Usage

### Endpoint:

```
POST /api/v1/resume/upload
```

### Swagger UI:

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

### Request Format:

* Content-Type: `multipart/form-data`
* Form field: `files` (send 1 or 2 files)
* Supported formats: `.pdf`, `.docx`

### Example Response:

```json
[
  {
    "filename": "resume1.pdf",
    "content_type": "application/pdf",
    "size_kb": 120.5,
    "status": "processed",
    "message": "File processed successfully.",
    "preview": "John Doe\nSoftware Engineer..."
  },
  {
    "filename": "notes.txt",
    "status": "failed_validation",
    "error": "Invalid file type. Only PDF or DOCX files are allowed."
  }
]
```

---

## 🚪 Error Handling

* Uploading more than 2 files: `400 Bad Request`
* Invalid file type: `400 Bad Request`
* Internal parsing failure: `500 Internal Server Error`

---

## 🔧 Future Roadmap

* ✅ Extract structured fields: name, email, phone, skills, etc.
* ✅ Job description upload and matching
* ✅ AI/NLP scoring engine using spaCy or transformers
* ✅ Frontend dashboard (React or Next.js)
* ✅ MongoDB or PostgreSQL integration
* ✅ 🧠 Resume Summarizer (LLM Prompting)
* ✅ ⚖️ Job Match Analysis (RAG + LLM)

---

## 👨‍💼 Author

**Shivam Lahoti**
Graduate Student

[Shivam Lahoti-LinkedIn](https://www.linkedin.com/in/shivam-lahoti-2811501b1/)

---

## 📃 License

MIT License. You are free to use, modify, and distribute this software.
