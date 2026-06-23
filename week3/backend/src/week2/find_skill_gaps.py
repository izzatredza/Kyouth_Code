import os
import sqlite3
import json
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()


# Define the Pydantic BaseModel exactly as requested
class SkillGapResult(BaseModel):
    gaps: List[str]


def get_unique_skills_from_db(db_url: str) -> set:
    """Reads the jobs table and extracts a unique set of clean, lowercase skills."""
    all_skills = set()

    try:
        with sqlite3.connect(db_url) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT tech_stack FROM jobs WHERE tech_stack IS NOT NULL AND tech_stack != ''"
            )
            rows = cursor.fetchall()

            for row in rows:
                tech_stack_string = row[0]
                parts = tech_stack_string.split(",")

                for part in parts:
                    clean_part = part.strip().lower()
                    if not clean_part:
                        continue

                    # Mandatory rule: Separate all skills with a '/' except protected terms
                    if (
                        "/" in clean_part
                        and clean_part != "a/b testing"
                        and clean_part != "ci/cd"
                    ):
                        sub_skills = clean_part.split("/")
                        for sub_skill in sub_skills:
                            sub_clean = sub_skill.strip()
                            if sub_clean:
                                all_skills.add(sub_clean)
                    else:
                        all_skills.add(clean_part)

    except sqlite3.Error:
        print("Database Error: Could not read skills from database.")

    return all_skills


def extract_skills_from_resume_with_ai(resume_text: str) -> set:
    """Uses Gemini to identify and extract technical skills from the resume text."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is missing!")
        return set()

    client = genai.Client()

    # Create a clear prompt telling Gemini exactly what to pull
    prompt = "You are a technical recruiter. Extract all core technical skills, programming languages, databases, "
    prompt += "and frameworks mentioned in this resume text. Ignore soft skills like leadership, management, cooking, or languages like English.\n\n"
    prompt += "Resume Text:\n" + resume_text

    # Prompt Optimization Technique: Enforce a strict JSON Schema string list output
    # This keeps responses extremely token-efficient and clean
    schema = {"type": "ARRAY", "items": {"type": "STRING"}}

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.0,  # Setting temperature to 0.0 helps promote determinism
            ),
        )

        # Safely convert the JSON string response back to a Python list
        extracted_list = json.loads(response.text)

        # Clean and normalize every skill found by the AI to lowercase
        cleaned_resume_skills = set()
        for skill in extracted_list:
            clean_skill = skill.strip().lower()
            if clean_skill:
                cleaned_resume_skills.add(clean_skill)

        return cleaned_resume_skills

    except Exception as e:
        print("AI Extraction Error occurred:", e)
        return set()


def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
    # 1. Check if the resume file exists
    if not os.path.exists(input_file_path):
        print("Error: Resume file not found at " + input_file_path)
        return SkillGapResult(gaps=[])

    # 2. Read resume content
    try:
        with open(input_file_path, "r", encoding="utf-8") as f:
            resume_content = f.read()
    except Exception:
        print("Error: Could not read the resume file.")
        return SkillGapResult(gaps=[])

    # 3. Use Gemini to extract the skills from the text
    resume_skills = extract_skills_from_resume_with_ai(resume_content)

    #  Post-filtering Alias Correction: Normalize variations like 'mysql' to ensure 'sql' matches
    if "mysql" in resume_skills:
        resume_skills.add("sql")

    # 4. Get the benchmark skills list from our database data
    required_skills = get_unique_skills_from_db(db_url)
    if not required_skills:
        print("Warning: No skills found in database tech_stack column.")
        return SkillGapResult(gaps=[])

    missing_skills = []

    # 5. Deterministic Matching Algorithm (Post-filtering)
    # Instead of letting an AI guess the missing pieces, your code computes it exactly
    blacklist = ["git", "github", "github actions", "gitlab", "gitlab ci", "ci/cd"]

    for skill in required_skills:
        if skill in blacklist:
            continue

        if skill not in resume_skills:
            missing_skills.append(skill)

    # 6. Sort the final output alphabetically as requested
    missing_skills.sort()

    return SkillGapResult(gaps=missing_skills)


if __name__ == "__main__":
    DATABASE_PATH = "data/jobs_d1.db"
    RESUME_PATH = "data/resume_d3.txt"

    print("Running AI-powered deterministic skill gap analysis...")
    result = find_skill_gaps(RESUME_PATH, DATABASE_PATH)

    print("\n--- Identified Skill Gaps ---")
    print("gaps =", result.gaps)
