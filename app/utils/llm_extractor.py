import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def enrich_llm_response(resume_text: str, extracted_fields:dict) ->dict:
    prompt= f"""
                You are an AI assistant that helps extract structured data from resumes.
                Given the resume text below and the partially extracted data, improve and fill missing fields.

                Resume Text:
                \"\"\"{resume_text}\"\"\"
            Existing extracted fields:
            {extracted_fields}

            Return only the updated structured fields in JSON format with keys:
            ["name", "email", "phone", "linkedin", "github", "skills", "address"]
                """
    try:
        response = model.generate_content(prompt)
        return eval(response.text)  # Safely parse if response is valid JSON
    except Exception as e:
        print("LLM enrichment failed:", e)
        return extracted_fields
    
