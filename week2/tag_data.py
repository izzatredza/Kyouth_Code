import os
import time
import asyncio
import ast
from dotenv import load_dotenv
from fastmcp import Client
from google import genai

load_dotenv()


async def tag_data(db_url: str):
    start_time = time.time()

    job_no = 0

    # Verify environment key first
    if not os.getenv("GEMINI_API_KEY"):
        print("[Error] GEMINI_API_KEY environment variable is not defined.")
        return

    # Initialize standard clients
    mcp_client = Client("db_server.py")
    gemini_client = genai.Client()

    async with mcp_client:
        db_raw_response = await mcp_client.call_tool(
            "fetch_untagged_jobs",
            {"limit": 8},
        )

        # FastMCP tool responses wrap data inside content blocks; extract the string text
        jobs_data_str = (
            db_raw_response[0].text
            if isinstance(db_raw_response, list)
            else str(db_raw_response)
        )

        # Quick validation check
        if "[]" in jobs_data_str or not jobs_data_str:
            print("No data to tag")
            print(
                f"Total tokens used: 0, took {(time.time() - start_time) * 1000:.3f}ms"
            )
            return

        prompt = f"""
        You are a technical data extraction assistant. 
        Analyze the following list of job tuples (source_id, description):
        {jobs_data_str}

        For each job tuple, extract the core technical stack as a concise, comma-separated list.
        Respond STRICTLY with a valid Python dictionary mapping where keys are the job IDs (integers) and values are the comma-separated strings.
        Do not add Markdown formatting wrappers, conversational descriptions, or fluff. make no mistake 

        Example target output format:
        {{1: "Python, SQL, Tableau", 2: "Java, Spring Boot, Docker"}}
        """

        print("Analyzing text features using Gemini...")
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        clean_text = (
            response.text.strip()
            .replace("```python", "")
            .replace("```json", "")
            .replace("```", "")
        )

        try:
            tags_map = ast.literal_eval(clean_text)
        except Exception as parse_error:
            print(
                f"[Parsing Error] Failed to read Gemini payload layout: {parse_error}"
            )
            print(f"Raw response was: {response.text}")
            return

        # 3. Iterate through mapping targets and execute individual write updates back via MCP
        print("Committing analytical tags back to database...")
        for job_id, tech_stack in tags_map.items():
            # Trigger write command via MCP tool
            await mcp_client.call_tool(
                "update_job_tech_stack",
                {"job_id": int(job_id), "tech_stack": str(tech_stack)},
            )
            job_no += 1
            print(f"Analyzed Job {job_no}: {tech_stack}")

    # Calculate token count metrics from metadata blocks
    total_tokens = 0
    if response.usage_metadata:
        total_tokens = (
            response.usage_metadata.prompt_token_count
            + response.usage_metadata.candidates_token_count
        )

    elapsed_ms = (time.time() - start_time) * 1000
    print(f"\nTotal tokens used: {total_tokens}, took {elapsed_ms:.3f}ms")


if __name__ == "__main__":
    asyncio.run(tag_data("jobs_d1.db"))
