import os
import re
import sqlite3
from typing import List
from pydantic import BaseModel


class SkillGapResult(BaseModel):
    gaps: List[str]


def get_unique_skills_from_db(db_url: str) -> set:
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

                    all_skills.add(clean_part)

    except sqlite3.Error:
        print("Database Error: Could not read skills from database.")

    return all_skills


def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:

    # 1. Check if the resume file exists
    if not os.path.exists(input_file_path):
        print("Error: Resume file not found at " + input_file_path)
        return SkillGapResult(gaps=[])

    # 2. Read resume content and normalize to lowercase
    try:
        with open(input_file_path, "r", encoding="utf-8") as f:
            resume_text = f.read().lower()
    except Exception:
        print("Error: Could not read the resume file.")
        return SkillGapResult(gaps=[])

    # 3. Get the benchmark skills list from our Day 2 database data
    required_skills = get_unique_skills_from_db(db_url)
    if not required_skills:
        print("Warning: No skills found in database tech_stack column.")
        return SkillGapResult(gaps=[])

    missing_skills = []

    # 4. Deterministic Matching using Regular Expressions
    for skill in required_skills:
        # Escape special characters (like C++) so regex doesn't break
        escaped_skill = re.escape(skill)

        if skill.endswith("+") or skill.endswith("#"):
            pattern = r"\b" + escaped_skill
        else:
            pattern = r"\b" + escaped_skill + r"\b"

        # Check if the skill is present in the resume text
        if not re.search(pattern, resume_text):
            missing_skills.append(skill)

    # 5. Sort the final output alphabetically
    missing_skills.sort()

    return SkillGapResult(gaps=missing_skills)


if __name__ == "__main__":
    # Test execution setup
    DATABASE_PATH = "data/jobs_d1.db"
    RESUME_PATH = "data/resume_d3.txt"

    print("Running deterministic skill gap analysis...")
    result = find_skill_gaps(RESUME_PATH, DATABASE_PATH)

    print("\n--- Identified Skill Gaps ---")
    print("gaps =", result.gaps)
