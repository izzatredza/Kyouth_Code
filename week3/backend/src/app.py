import os
import sys
import importlib.util
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── BULLETPROOF PATH RESOLUTION ───
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Dynamically import week2 module using your working spec method
FIND_SKILL_GAPS_PATH = os.path.join(CURRENT_DIR, "week2", "find_skill_gaps.py")
spec = importlib.util.spec_from_file_location("find_skill_gaps", FIND_SKILL_GAPS_PATH)
find_skill_gaps = importlib.util.module_from_spec(spec)
if spec.loader is None:
    raise ImportError(f"Cannot load module from {FIND_SKILL_GAPS_PATH}")
spec.loader.exec_module(find_skill_gaps)
analyze_raw_text_gaps = find_skill_gaps.analyze_raw_text_gaps

# 2. Point to exactly where jobs_d1.db lives inside your week2 subfolder
DATABASE_PATH = os.path.join(CURRENT_DIR, "week2", "data", "jobs_d1.db")

# Double check in server logs on container bootup to verify pathing
print(f"[DEBUG MASTER] Checking DB existence at: {DATABASE_PATH}")
print(f"[DEBUG MASTER] DB Exists status: {os.path.exists(DATABASE_PATH)}")


class ChatRequest(BaseModel):
    message: str
    pdf_text: str = ""


@app.post("/chat")
async def chat(payload: ChatRequest):
    try:
        user_message = payload.message.strip().lower()
        resume_context = payload.pdf_text

        # Target Case: Evaluator requests the skills gap analysis
        if "skills gap" in user_message or "skill gap" in user_message:
            if not resume_context:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "reply": "Please upload a resume PDF file first before requesting a skills gap check."
                    },
                )

            # Crash protection check: verify the file can actually be opened
            if not os.path.exists(DATABASE_PATH):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "reply": f"Backend Error: Database file not found at container path {DATABASE_PATH}"
                    },
                )

            # Compute gaps using your deterministic comparison module
            analysis = analyze_raw_text_gaps(resume_context, DATABASE_PATH)

            # If the database read returned skills, but there are zero gaps
            if not analysis.gaps:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "reply": "Excellent! No missing technical skills identified compared to our database baseline profiles."
                    },
                )

            # Format and respond exactly like your week 2 sample screen
            formatted_gaps = " - ".join(analysis.gaps)
            reply_text = f"Skills gap identified: - {formatted_gaps}"

            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"reply": reply_text}
            )

        # Standard AI Conversational Fallback
        client = genai.Client()
        full_context = user_message
        if resume_context:
            full_context = f"Context from uploaded resume:\n{resume_context}\n\nUser Request: {payload.message}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_context,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"reply": response.text}
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"reply": f"Internal system processing error: {str(e)}"},
        )
