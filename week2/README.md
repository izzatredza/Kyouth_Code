# Data Tagging & Skill Gap Analysis System

## Project Overview
The goal of this project is to build an automated data enrichment and analysis pipeline for job postings and resumes. The system is split into two core phases:
1. **Data Tagging:** Scanning unstructured job descriptions from an SQLite database and using Gemini 2.5 Flash through an MCP (Model Context Protocol) Server connection to extract and save clean technical stacks.
2. **Skill Gap Analysis:** Running a 100% deterministic text-matching algorithm to cross-reference an extracted candidate resume against the database skills to identify clear professional gaps.


## Setup Instructions

### Prerequisites
* **Python Version:** Python 3.12 or higher
* **Package Manager:** `uv` (Fast Python package installer)
* **API Key:** Google AI Studio Gemini API Key
* **Ollama:** Ollama software 0.21.*


### Installation & Environment Setup
1. Download the **Ollama software** at https://github.com/ollama/ollama/releases/tag/v0.21.3-rc0 and download the **OllamaSetup.exe** file

2. Once the install is complete go to powershell and use this command:
    ```bash
    ollama pull llama3.1
    ollama pull phi3
    ollama pull deepseek-r1:1.5b
    ollama pull gemma
    ```

3. Go to **Google AI Studio** make an account and create your **API key**


4. Go to **Enviroment Variable** at your local computer and click new. Put the name as **GEMINI_API_KEY** and put **API KEY** value at the value text box


5. Clone the github repo:
    ```bash
    git clone https://github.com/izzatredza/Kyouth_Code.git
    ```

6. Create enviroment and install dependencies
From the `week2` directory:

    ```bash
    cd week2
    uv sync
    ```
   Now you good and ready to go

### Running the code

1. **prompt_mode.py**

- run the code using this format

    ```bash
    uv run prompt_mode.py <model> "prompt"
    ```

    Expected Output of : 
    ```bash
    uv run prompt_mode.py gemini-2.5-flash "Tell me a joke"
    ```                       

    ```text
    --- RESPONSE ---

    Why don't scientists trust atoms?

    Because they make up everything!
    ```

   the model that is available are ***llama3.1 , phi3, deepseek-r1:1.5b, gemma, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-3-flash-preview**

2. **tag_data.py**

- Download the **resource.zip** file here https://fxdigitalskills.notion.site/Day-1-2-Tagging-52b329ef40524159b3beab5858275976

- Extract it and put the file at data folder in `week2` (create the `data` folder first)

- Run the command
    ```bash
    uv run tag_data.py
    ```

    - Expected Output:
    ```text
    Analyzed Job 1: Python, SQL, R, Java, Shell, ETL, Data Warehousing, Data Lake, Tableau, PowerBI, DataStudio, LLM, Deep Learning
    Analyzed Job 2: Java, Spring Boot, Python, SQL, PyTorch, TensorFlow, scikit-learn, Microservices, REST API, Git, CI/CD, Docker, Kubernetes, AWS, Azure, GCP, MLOps, Kafka, Redis
    ....
    ```

3. **find_skill_gaps.py**

    - Run the command
    ```bash
    uv run find_skill_gaps.py
    ```

    - Expected Output:
    ```text
    --- Identified Skill Gaps ---
    gaps = ['alibaba cloud', 'api', 'aws', 'ci/cd', 'data automation', 'data engineering', 'data extraction', 'data lake', 'data normalization', 'data pipeline', 'data validation', 'data warehousing', 'datastudio', 'deep learning', 'docker', 'etl', 'fastapi', 'flask', 'gcp', 'git', 'github actions', 'google cloud', 'grafana', 'java', 'kafka', 'kubernetes', 'langchain', 'linux', 'llamaindex', 'llm', 'microservices', 'mlops', 'mongodb', 'nginx', 'node.js', 'php', 'postgresql', 'power bi', 'powerbi', 'prometheus', 'pytorch', 'r', 'rag', 'redis', 'rest api', 'scikit-learn', 'shell', 'spring boot', 'sql', 'tableau', 'tensorflow', 'web automation']
    ....
    ```

 ## API / Function Reference

 ### 1. db_server.py (MCP Server Wrapper)

   **fetch_untagged_jobs() -> str**

    Purpose: Queries the SQLite database for job rows where tech_stack is blank or null.

    Outputs: Returns a JSON string representation of a list of data tuples [(source_id, description), ...].

   **update_job_tech_stack(job_id: int, tech_stack: str) -> str**

    Purpose: Saves the model-extracted technical stack strings directly back into the database table row.

    Inputs: job_id (integer target key) and tech_stack (comma-separated string).

 ### 2. **tag_data.py (MCP Client Processing Core)**

   **tag_data(db_url: str)**

    Purpose: Coordinates the execution. Connects to db_server.py, passes descriptions to gemini-2.5-flash, cleans up text outputs, and pushes changes back.

 ### 3. **find_skill_gaps.py (Deterministic Analyzer)**

   **find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult**

    Purpose: Compares target resume strings with required database features using strict word boundary algorithms.

    Outputs: Returns a validated Pydantic SkillGapResult object containing lowercase, sorted missing skills.

 ## Data / Assumptions

### 1. Database Schema (jobs table)

    source_id (TEXT PRIMARY KEY): Unique identifier for each job.

    description (TEXT): Unstructured raw job post data.

    tech_stack (TEXT): Target column populated by our pipeline with comma-separated words.

### 2. System Assumptions & Data Flow

 ```Data Flow: Database -> MCP Server Tool -> Client Orchestrator -> Gemini Model API -> Clean Dict Parsing -> MCP Update Tool -> Saved in Database.```

 The '/' Splitting Convention: Composite strings like AWS/Azure/GCP are safely stripped down into separate skills. Protected terms like A/B testing and CI/CD are explicitly preserved.

 Simplification: Non-technical terms (e.g., 'management', 'leadership') and formal certifications are safely bypassed to focus strictly on technical engineering assets.

### 3. Testing

 Verification Method: Verified by inspecting database outputs inside a database viewer (DB Browser for SQLite) to ensure changes write perfectly.

 Determinism Testing: Checked by running find_skill_gaps.py multiple consecutive times. Because it avoids generative AI text modeling during matching and uses native Python Regular Expressions instead, it returns identical, stable arrays on every single run.

 Boundary Validation: Tested with edge-case skills containing unique programming symbols (like C++ or C#) to make sure they match correctly without bleeding into random words like "cloud" or "docker".

### 4. Limitations

 Rate Limits: Since we are using standard free-tier Gemini API parameters (10 Requests Per Minute), attempting to run the data tagging script on thousands of rows simultaneously without setting a loop delay could trigger a `429 Resource Exhausted block`.

 Formatting Vulnerability: If Gemini outputs an invalid format layout instead of a clean python dictionary syntax string, the `ast.literal_eval()` method in `tag_data.py` will catch the error and stop processing to avoid a full script crash.

 ## Architecture Reflection

 **Design Choices**

 I structured this system into an MCP Server/Client model (`db_server.py` and `tag_data.py`) to isolate the database reading and writing activities from the AI prompt logic. This separation of concerns means that if the database structure changes in the future, only the server script needs to be modified, while the client analysis code remains completely untouched.

 **Trade-offs**

 Determinism vs. Flexibility: For the skill gap analysis, I chose Regular Expressions over an LLM. This choice guaranteed 100% deterministic, reproducible, and cost-free matching accuracy at the cost of missing semantic matches (e.g., it will flag a gap if a job says "GCP" but a resume says "Google Cloud Platform").

 ## Future Improvements

 Given more time, I would

  - Implement a way to use different gemini model and ollama model to tag the data

  - Build an alias-mapping dictionary (e.g., mapping "Google Cloud Platform" to "GCP") into the matching engine to capture semantic synonyms without sacrificing determinism.

