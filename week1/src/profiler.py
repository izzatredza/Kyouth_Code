import sqlite3


def run_data_profile(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n--- 🔍 DATA QUALITY REPORT ---")

    # Example: Count total number of jobs
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]
    print(f"📈 Total Records: {total_jobs}")

    # Example: Count jobs by company
    cursor.execute("""
            SELECT 
                SUM(CASE WHEN job_title IS NULL OR job_title = '' THEN 1 ELSE 0 END),
                SUM(CASE WHEN company IS NULL OR company = '' THEN 1 ELSE 0 END),
                SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END)
            FROM jobs
        """)

    missing_job_title, missing_company, missing_description = cursor.fetchone()

    print(
        f"❓ Missing Values -> job_title: {missing_job_title or 0}, company: {missing_company or 0}, description: {missing_description or 0}"
    )

    cursor.execute("SELECT CAST(AVG(LENGTH(description)) AS INT) FROM jobs")
    avg_description_length = cursor.fetchone()[0]
    print(f"📝 Average Description Length: {avg_description_length}")

    cursor.execute(
        """ SELECT Length(description) as len FROM jobs WHERE description IS NOT NULL ORDER BY len ASC LIMIT 1 """
    )
    min_description_length = cursor.fetchone()[0]
    print(f"⚠️  Minimum Description Length: {min_description_length}")

    cursor.execute(
        """ SELECT Length(description) as len FROM jobs WHERE description IS NOT NULL ORDER BY len DESC LIMIT 1 """
    )
    max_description_length = cursor.fetchone()[0]
    print(f"🚨  Maximum Description Length: {max_description_length}")

    # Example: Count jobs by location
    cursor.execute("SELECT location, COUNT(*) FROM jobs GROUP BY location")
    jobs_by_location = cursor.fetchall()
    print("Jobs by Location:")
    for location, count in jobs_by_location:
        print(f"{location}: {count}")

    conn.close()
