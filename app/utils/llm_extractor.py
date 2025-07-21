import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

SOFT_SKILLS = {"communication", "stakeholder management", "project management"}

def enrich_llm_response(resume_text: str, extracted_fields: dict) -> dict:
    prompt = f"""
    You are an AI assistant that extracts structured information from resumes.
    Given the resume text and existing extracted fields, return a complete JSON object
    with the keys: ["name", "email", "phone", "linkedin", "github", "skills", "address"].

    Ensure that the 'skills' field includes relevant soft skills such as:
    communication, stakeholder management, and project management — if contextually implied.

    Resume Text:
    \"\"\"{resume_text}\"\"\"
    Existing extracted fields:
    {json.dumps(extracted_fields)}

    Return valid JSON only.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean up markdown wrappers
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        logger.info("LLM Resume Response:\n%s", text)
        llm_data = json.loads(text)

        # Normalize and clean skills
        skills = llm_data.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]
        elif not isinstance(skills, list):
            skills = []

        # Add missing soft skills if not already included
        skill_set = {s.lower() for s in skills}
        for soft_skill in SOFT_SKILLS:
            if soft_skill not in skill_set:
                skills.append(soft_skill)

        llm_data["skills"] = skills

        # Ensure all fields are present
        for field in ["name", "email", "phone", "linkedin", "github", "address"]:
            llm_data[field] = llm_data.get(field, "Not Available")

        logger.info("LLM enriched skills: %s", skills)
        return llm_data

    except Exception as e:
        logger.warning("LLM resume enrichment failed: %s", e)
        return {
            "name": "Not Available",
            "email": "Not Available",
            "phone": "Not Available",
            "linkedin": "Not Available",
            "github": "Not Available",
            "skills": list(SOFT_SKILLS),
            "address": "Not Available"
        }


def enrich_jd_skills_with_llm(jd_text: str, extracted_skills: list[str]) -> list[str]:
    prompt = f"""
    You are an AI assistant that extracts required skills from job descriptions.
    Given the job description and the initially extracted skills, return a JSON list
    of all required technical and soft skills. Include skills like communication, stakeholder
    management, and project management if implied in the context.

    JD Text:
    \"\"\"{jd_text}\"\"\"
    Initially extracted skills:
    {json.dumps(extracted_skills)}

    Return only a clean JSON list.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        logger.info("LLM JD Response:\n%s", text)

        if text.startswith("[") and text.endswith("]"):
            try:
                jd_skills = json.loads(text)
                if isinstance(jd_skills, list):
                    return [s.strip().lower() for s in jd_skills if isinstance(s, str)]
            except json.JSONDecodeError:
                pass

        # Fallback: parse comma-separated string manually
        jd_skills = text.strip("[]").split(",")
        return [s.strip().lower().strip('"') for s in jd_skills if s.strip()]

    except Exception as e:
        logger.warning("LLM JD enrichment failed: %s", e)
        return [s.lower() for s in extracted_skills]
    


def generate_llm_recommendation(jd_keywords: set, resume_keywords: set, missing_keywords: list[str]) -> str:
    """
    Generate a short, actionable recommendation based on missing JD keywords in the resume.
    """
    try:
        prompt = f"""
            You are an AI assistant helping job seekers improve their resumes.

            Here are the keywords extracted from the job description:
            {sorted(jd_keywords)}

            Here are the keywords extracted from the candidate's resume:
            {sorted(resume_keywords)}

            The following important keywords are missing from the resume:
            {missing_keywords}

            Based on this, provide a short, actionable recommendation on how the candidate can improve their resume to better match the job description.
            Do not return JSON. Just return a human-friendly recommendation.
        """
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.warning("LLM recommendation generation failed: %s", e)
        return "LLM recommendation could not be generated."
