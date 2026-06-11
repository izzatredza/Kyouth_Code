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
        with open(file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        source_id = soup.find("meta", property="og:url", content=True)
        if source_id:
            url_string = source_id["content"]
            source_id = url_string.strip().strip("/").split("/")[-1]
        else:
            source_id = None
            skipped += 1
            print(f"⚠️ Missing source_id in: {file.name}")
            continue  # Skip processing this file if source_id is missing

        job_title = soup.find("meta", property="og:title", content=True)
        if job_title:
            job_title = job_title["content"].split(" - ")[0].strip()
        else:
            job_title = None
            skipped += 1
            print(f"⚠️ Missing job_title in: {file.name}")
            continue  # Skip processing this file if job_title is missing

        company = soup.find(attrs={"data-automation": "advertiser-name"})
        if company:
            company = company.get_text().strip()
        else:
            company = None
            skipped += 1
            print(f"⚠️ Missing company in: {file.name}")
            continue  # Skip processing this file if company is missing

        desc_container = soup.find(attrs={"data-automation": "jobAdDetails"})
        if (
            desc_container
            and desc_container.get_text(separator=" ", strip=True).strip()
        ):
            for script in desc_container(["script", "style"]):
                script.decompose()
            description = desc_container.get_text(separator=" ", strip=True)
        else:
            description = None
            skipped += 1
            print(f"⚠️ Missing description in: {file.name}")
            continue  # Skip processing this file if description is missing

        if source_id == "" or job_title == "" or company == "" or description == "":
            skipped += 1
            continue  # Skip processing this file if any field is empty
        else:
            print(f"✅ Processed: {file.name}")

        try:
            job = Job(
                source_id=source_id,
                job_title=job_title,
                company=company,
                description=description,
            )

            json_output_file = output_path / f"{file.stem}.json"

            with open(json_output_file, "w", encoding="utf-8") as f:
                f.write(job.model_dump_json(indent=4))
                print(f"✅ Processed: {file.name}")
                processed += 1

        except ValidationError as e:
            print(f"⚠️ Validation errors: {e}")
            skipped += 1
            continue  # Jump to the next file if an exception happens

    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")
