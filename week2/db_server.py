import sqlite3
from fastmcp import FastMCP

mcp = FastMCP("SQLite-Service")
DB_PATH = "data/jobs_d1.db"


@mcp.tool
def fetch_untagged_jobs(limit: int = 8) -> str:
    """Fetches a specific number of jobs where tech_stack is empty."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT source_id, description FROM jobs 
                WHERE tech_stack IS NULL OR tech_stack = '' 
                LIMIT ?
            """,
                (limit,),
            )
            return str(cursor.fetchall())
    except sqlite3.Error as e:
        return f"[]"


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
            return f"Success"
    except sqlite3.Error as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run()
