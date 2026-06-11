from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError


class Job(BaseModel):
    source_id: str = Field(..., description="Unique identifier for the job posting")
    job_title: str = Field(..., description="Title of the job position")
    company: str = Field(..., description="Name of the company offering the job")
    description: str = Field(..., description="Description of the job responsibilities")


def process_all_html(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    html_files = list(input_path.glob("*.html"))
    print("🥈 Silver...")

    total = len(html_files)
    processed = 0
    skipped = 0

    for file in html_files:
        # Wrap everything in a general try/except to avoid loop-breaking crashes
        try:
            with open(file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # 1. Extract Source ID
            source_id_tag = soup.find("meta", property="og:url", content=True)
            if not source_id_tag:
                print(f"⚠️ Missing source_id in: {file.name}")
                skipped += 1
                continue
            source_id = source_id_tag["content"].strip().rstrip("/").split("/")[-1]

            # 2. Extract Job Title
            job_title_tag = soup.find("meta", property="og:title", content=True)
            if not job_title_tag:
                print(f"⚠️ Missing job_title in: {file.name}")
                skipped += 1
                continue
            job_title = job_title_tag["content"].split(" - ")[0].strip()

            # 3. Extract Company
            company_tag = soup.find(attrs={"data-automation": "advertiser-name"})
            if not company_tag:
                print(f"⚠️ Missing company in: {file.name}")
                skipped += 1
                continue
            company = company_tag.get_text().strip()

            # 4. Extract Description
            desc_container = soup.find(attrs={"data-automation": "jobAdDetails"})
            if not desc_container:
                print(f"⚠️ Missing description container in: {file.name}")
                skipped += 1
                continue

            for script in desc_container(["script", "style"]):
                script.decompose()
            description = " ".join(desc_container.get_text(separator=" ").split())

            # Check for empty field strings
            if not all([source_id, job_title, company, description]):
                print(f"⚠️ Empty required field values in: {file.name}")
                skipped += 1
                continue

            # Pydantic Validation & File Saving
            job = Job(
                source_id=source_id,
                job_title=job_title,
                company=company,
                description=description,
            )

            json_output_file = output_path / f"{file.stem}.json"
            json_output_file.write_text(job.model_dump_json(indent=4), encoding="utf-8")

            print(f"✅ Processed: {file.name}")
            processed += 1

        except ValidationError as ve:
            print(f"⚠️ Validation error in {file.name}: {ve}")
            skipped += 1
        except Exception as e:
            # Captures unexpected system or parsing errors without crashing the entire run
            print(f"❌ Unexpected error processing {file.name}: {e}")
            skipped += 1

    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")
