# Resume Helper Chatbot - Technical Manual & Documentation

This repository contains a full-stack, containerized application designed to assist job seekers by extracting technical data from an uploaded resume and identifying critical skill gaps against local career baseline data profiles.

---

## 1. Project Overview
The core objective of this project is to architect, build, and containerize a modern, decentralized full-stack chat application. The application breaks down into isolated microservices:
* **Frontend UI:** A clean HTML/Bootstrap web page serving an interactive interface for file uploads and user prompts.
* **Backend API Engine:** A fast FastAPI server running on an isolated virtual network layer.
* **AI Integration Module:** An extraction engine that uses the official Google GenAI SDK to parse text representations and execute a custom deterministic matching algorithm against historical target job listings.

---

## 2. Setup Instructions

### Prerequisites
Make sure your host evaluation machine has the following tools installed before beginning setup:
* **Docker Desktop** (or Docker Engine version 20.10.0 or higher)
* **Docker Compose** (version v2.0.0 or higher)
* *(Optional Local Triage)* **uv** (Python package installer engine)

### Environment Configuration
1. Navigate to the root folder of the project (`week3/`).
2. Create a file named `.env` in the root folder (or inside the `backend/` directory depending on your local terminal execution context).
3. Open the `.env` file and insert your API credentials exactly like this:

```text
GEMINI_API_KEY=your_actual_google_gemini_api_key_here
```

Security Note: The .env file is explicitly blocked from Git tracking via .gitignore and omitted from image building processes via .dockerignore to completely eliminate credential leaks.

## 3. Usage
Launching the Infrastructure

To orchestrate, build, and turn on the entire environment simultaneously via a single network switch layer, execute the following command in your terminal root:
Bash

docker compose up --build

Accessing the Web Interface

Once the container logs indicate that the Uvicorn engine has stabilized, open your local web browser and go to:
👉 http://localhost:8000
Expected Inputs & Workflow Behaviors

    Standard Conversation: Type standard text inputs into the chat box (e.g., "Hello" or "Summarize my experience"). The system returns an expressive response from the generative model layer.

    PDF Assessment Upload: Click Browse... to choose a standard resume file. The frontend captures and extracts structural text fields directly out of the context bodyspace.

    Deterministic Skill Evaluation: Type the phrase "find skills gap" into the input layout box. The backend skips standard conversational fallback generation, interfaces directly with the SQLite file, maps the text requirements, and prints out an alphabetized string list of structural gaps.

## 4. API / Function Reference
Backend Endpoints: POST /chat

Exposes the core request router interface used by the frontend network bridge.

    Expected JSON Input Payload (ChatRequest):
    JSON

    {
      "message": "string",
      "pdf_text": "string (optional raw parsed resume content)"
    }

    JSON Response Output Format:
    JSON

    {
      "reply": "string containing either skill gap array printouts or generic chatbot outputs"
    }

Frontend JavaScript Core Functionality

    Form Submission Interceptor (chat-form Event Listener): Intercepts standard submit signals, suppresses default window reload patterns using e.preventDefault(), pulls localized text inputs, references parsed PDF string components, and performs an asynchronous fetch() network post out to port 8001.

Docker Network Architecture Communication

The system explicitly avoids using the insecure host network driver configuration. Instead, it provisions an isolated software bridge abstraction called app-network. Containers communicate via virtual proxy forwarding, securely binding incoming external host requests on ports 8000 and 8001 directly through the container runtime boundaries.

## 5. Data / Assumptions
System Data Flows
Plaintext

[ Browser UI ] ──(POST /chat JSON Payload)──> [ Port 8001 Bridge ] ──> [ FastAPI Router ]
                                                                                │
   ┌────────────────────────────────────────────────────────────────────────────┤
   ▼ (Trigger Text Check)                                                       ▼ (Fallback Chat)
[ analyze_raw_text_gaps ] ──> [ SQLite jobs_d1.db ]                     [ Gemini-2.5-Flash ]

Core Constraints & Logic Simplifications

    Input Expectations: The interface assumes the uploaded PDF is standard, clean, unencrypted text. Document scans or complex multiple-column canvas designs might degrade the accuracy of the frontend text extraction tools.

    Stateless Processing Bounds: The data flow currently operates under a bare-minimum stateless execution protocol. Prompts do not pass state timelines backwards across active click instances; each submission delivers a fresh verification envelope.

    Week 2 Integration Strategy: Instead of executing a heavy local LLM that might hang or crash evaluation machines, the system queries the local jobs_d1.db SQLite structure directly to run a fast, deterministic post-filtering matching algorithm.

## 6. Testing
Backend Testing Triage (curl)

To verify the health and path resolution of the backend server independently of the web browser UI layout, run this command in an isolated terminal window:
Bash

curl -X POST "http://localhost:8001/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'

Expected Output: A structured status 200 OK response mapping featuring a valid string reply from the engine.
Frontend UI Verification

    File Isolation Test: Verify that selecting a PDF successfully populates the filename indicator tracking layer on screen.

    Layout Clearing Test: Verify that clicking Send resets both the text entry zone string value and the chosen file reference target area instantly to prevent prompt duplication.

## 7. Limitations & Boundary Conditions

    Lack of State Preservation: The system intentionally runs a bare-minimum conversation tracking framework. Following up on an output with contextual terms like "What should I learn first based on that?" causes the engine to lose focus, as previous dialogue turns are not written into an ongoing historical array structure.

    Authentication Bounds: There is no user authentication, token rate limiting, or tracking. The endpoint layout is exposed directly on the local network.

    Alias Extraction Gaps: The deterministic comparison engine relies heavily on string mapping comparisons. If a resume lists “Advanced Query Writing” and the database requires “SQL”, the matching logic will flag it as a skill gap unless explicit hardcoded aliases (like matching MySQL to SQL) catch it.

## 8. Architecture Reflection
Design Choices & Containerization

Decoupling the architecture into separated frontend and backend microservices ensures a highly maintainable, modern development lifecycle.

Containerizing the modules using separate Dockerfiles guarantees that the code runs identically on the student’s computer and the examiner's grading machine. It completely eliminates the notorious "it works on my machine" problem by packaging specific, isolated Linux system layers (python:3.14-bookworm) directly alongside the application code.
Trade-Off Valuations

This implementation prioritizes deployment stability, machine safety, and structural deterministic precision over raw open-ended AI generation:

    Cloud API vs. Local Ollama Processing: Moving from a heavy local model execution track to the cloud-hosted Gemini engine protects evaluation hardware from VRAM starvation and thermal throttling.

    Algorithmic Gap Checking: Instead of allowing a generative AI model to guess missing requirements (which often results in hallucinations), the code reads concrete historical parameters from jobs_d1.db and runs a strict mathematical comparison, ensuring highly accurate grading results.

Planned Improvements (Given More Time)

    State Database Injection: Introduce a lightweight key-value data storage container (such as Redis or a dedicated PostgreSQL chat history table) to cleanly preserve conversational context across multi-turn user dialogues.

    Robust Frontend Refactoring: Upgrade the unstyled HTML layout workspace into a modular component tree pattern using frameworks like React or Next.js to provide smoother, asynchronous user feedback loops.