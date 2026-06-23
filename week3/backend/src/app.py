from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load variables defined inside a local .env configuration file
load_dotenv()

app = FastAPI()

# Enable CORS so your Frontend (port 8000) can talk to your Backend (port 8001) smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the modern Gemini Client
# It automatically picks up GEMINI_API_KEY from the environment/system variables
client = genai.Client()


# Define the expected JSON payload format coming from the frontend JavaScript request
class ChatRequest(BaseModel):
    message: str
    pdf_text: str = ""


@app.post("/chat")
async def chat(payload: ChatRequest):
    try:
        user_prompt = payload.message
        resume_context = payload.pdf_text

        # Combine the user prompt with the extracted resume text if it exists
        full_context = user_prompt
        if resume_context:
            full_context = (
                f"Context from uploaded resume:\n{resume_context}\n\n"
                f"User Question: {user_prompt}"
            )

        # Call the lightweight, fast gemini-2.5-flash model
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
            content={"reply": f"Error communicating with Gemini engine: {str(e)}"},
        )
