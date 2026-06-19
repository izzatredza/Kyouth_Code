import os
import sqlite3
from fastmcp import FastMCP

mcp = FastMCP("SQLite-Service")
DB_PATH = "data/jobs_d1.db"


@mcp.tool
def fetch_untagged_jobs() -> str:
    """Fetches a specific number of jobs where tech_stack is empty."""

    if not os.path.exists(DB_PATH):
        print(f"[Server Error] Database file not found at {DB_PATH}")
        return "[]"

    try:
        with sqlite3.connect(f"file:{DB_PATH}?mode=rw", uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT source_id, description FROM jobs 
                WHERE tech_stack IS NULL OR tech_stack = '' 
            """,
            )
            return str(cursor.fetchall())
    except sqlite3.Error:
        print(f"[Server Error] Failed to fetch untagged jobs from {DB_PATH}")
        return "[]"


@mcp.tool
def update_job_tech_stack(job_id: int, tech_stack: str) -> str:
    """Updates the tech_stack column for a specific job ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE jobs SET tech_stack = ? WHERE source_id = ?
            """,
                (tech_stack, job_id),
            )
            conn.commit()
            return "Success"
    except sqlite3.Error:
        return "Error: Failed to update job tech stack"


if __name__ == "__main__":
    mcp.run()
