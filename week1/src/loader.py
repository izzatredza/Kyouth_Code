import json
import sqlite3
from pathlib import Path


def load_all_jsons(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    json_files = list(input_path.glob("*.json"))

    print("🥇 Gold...")

    db_path = output_dir / "jobs.db"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            job_title TEXT,
            company TEXT,
            description TEXT
        )
    """
    )

    connection.commit()

    total = len(json_files)
    inserted = 0
    skipped = 0

    for file in json_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            cursor.execute(
                """
                INSERT INTO jobs (source_id, job_title, company, description)
                VALUES (?, ?, ?, ?)
            """,
                (
                    data["source_id"],
                    data["job_title"],
                    data["company"],
                    data["description"],
                ),
            )
            connection.commit()

            # Insert or Ignore skips the file if the source_id is already in the DB
            cursor.execute(
                """
                INSERT OR IGNORE INTO jobs (source_id, job_title, company, description)
                VALUES (?, ?, ?, ?)
            """,
                (
                    data.get("source_id"),
                    data.get("job_title"),
                    data.get("company"),
                    data.get("description"),
                ),
            )

            print(f"✅ Inserted: {file.name}")
            inserted += 1

        except Exception as e:
            print(f"⚠️ Failed to insert {file.name}: {e}")
            skipped += 1

    print("\n📊 Gold Summary:")
    print(f"Total: {total} | Inserted: {inserted} | Skipped: {skipped}")
