# Job Postings Pipeline (ELT)

A simple Python-based data engineering pipeline that cleans raw job listings and loads them into a local database using the **Medallion Architecture**.

## 📂 Project Structure

```text
├── data/
│   ├── 1_bronze/         # Put your scraped .html files here
│   ├── 2_silver/         # Automatically generated clean .json files
│   └── 3_gold/           # Automatically generated SQLite database file (.db)
├── main.py               # The main script you run
└── README.md
```
🚀 Quick Start
1. Install Dependencies

You only need two external libraries to run this pipeline:
Bash

pip install beautifulsoup4 pydantic

2. Add Your Source Files

Download a folder named 0_source.zip at 
https://fxdigitalskills.notion.site/Day-1-Extractor-Bronze-Layer-35117c3c3ec080d5bee7d5f87355cbcd 

3. Run the Pipeline

Run the script from your terminal using one of the available commands:
Bash

# Show usage instruction
```
python main.py
```

# Run only a specific stage
```
python main.py ingest
python main.py process
python main.py load
python main.py profile
```
# Run the entire pipeline from start to finish
```
python main.py all
```

📊 Pipeline Stages

    Ingest (Bronze): Turn .mhtml to raw .html file.

    Process (Silver): Uses BeautifulSoup to parse out key details (ID, Title, Company, Description), normalizes messy text whitespace, and saves them into data-validated JSON profiles using Pydantic.

    Load (Gold): Connects to your SQLite database, automatically sets up your tables, checks for row duplicates, and safely saves your records.

    Profile: Generates a clean Data Quality Report directly from your database, showing record counts, missing values, and description lengths.
