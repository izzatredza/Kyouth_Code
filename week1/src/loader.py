import json
import sqlite3
from pathlib import Path


def load_all_jsons(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    json_files = list(input_path.glob("*.json"))

    print("🥇 Gold...")

    db_path = output_path / "jobs.db"  # Fixed: ensured output_path is a Path object
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            job_title TEXT,
            company TEXT,
            description TEXT,
            tech_stack TEXT
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
                INSERT OR IGNORE INTO jobs (source_id, job_title, company, description, tech_stack)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    data.get("source_id"),
                    data.get("job_title"),
                    data.get("company"),
                    data.get("description"),
                    data.get("tech_stack", ""),
                ),
            )
            connection.commit()

            if cursor.rowcount > 0:
                print(f"✅ Inserted: {file.name}")
                inserted += 1
            else:
                print(f"⏭️ Skipped (duplicate): {file.name}")
                skipped += 1

        except Exception as e:
            print(f"⚠️ Failed to process {file.name}: {e}")
            skipped += 1

    connection.close()

    print("\n📊 Gold Summary:")
    print(f"Total: {total} | Inserted: {inserted} | Skipped: {skipped}")
