# Job Postings Pipeline (ETL)
A simple Python-based data engineering pipeline that cleans raw job listings and load them into a local database using the **Medallion Architecture**.

# Project Setup

🚀 Quick Start
A. Install Dependencies

1) Install uv

## Windows
use powershell and enter this code:  
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
## Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```


## 2) Create environment and install dependencies
From the `week_1` directory:

```bash
cd week_1
uv sync
```

This will create/update the project environment and install dependencies from `pyproject.toml`.


## 3) Run the pipeline
Run the full flow (ingest -> process -> load -> profile):

```bash
uv run main.py all
```

Or run only profiling:

```bash
uv run main.py profile
```

# Usage

## Required inputs
- Place raw source files in `data/0_source` (you can get the 0_source at this address
 https://fxdigitalskills.notion.site/Day-1-Extractor-Bronze-Layer-35117c3c3ec080d5bee7d5f87355cbcd)

- Keep the expected folder structure under `data/`

## Command syntax

```bash
uv run main.py <command>
```

# Technical Reflection

### Day 1: The Extractor (Medallion & Lakehouses)
Preserving original raw HTML/MHTML assets in the Bronze layer provides an immutable "single source of truth." Web formatting and scraper selectors are highly volatile; if extraction requirements change later—such as needing to capture a newly requested field like salary bounds or review ratings—the engineering team can update the parsing logic and re-run the entire pipeline historically against the raw local files.

If raw data is discarded immediately upon database insertion, recovering from an undetected parsing bug or accommodating schema enhancements would require re-scraping live production web endpoints. This wastes bandwidth, risks hitting rate limits, and can result in permanent data loss if old web pages are taken down.

### Day 2: Treatment Plant (ETL vs ELT & Scale)
Modern cloud systems choose Extract-Load-Transform (ELT) because decoupling storage from compute enables them to ingest massive files at scale without blocking operations. Raw unstructured data can be dumped into scalable cloud object storage (like AWS S3) instantly, deferring the computational cost of cleaning and reshaping data to powerful cloud warehouses (like Snowflake or BigQuery) that optimize query scaling dynamically.


### Day 3: The Blueprint & The Vault (Storage & Contracts)
Reflections on Data Contracts and Idempotency:
When a foundational field like `job_title` disappears from source files, the system must fail early and loudly. Allowing incomplete entries to slip through silently pollutes down-stream analytics and downstream reporting platforms, leading to misleading metrics (e.g., calculations counting active job types yielding broken results). Implementing data contracts via Pydantic boundaries sets an active baseline that quarantines anomalies immediately before bad data can spread into production.

The `INSERT OR IGNORE` operation serves as a fundamental safeguard for data idempotency. In web scraping, processing identical records multiple times across scheduling boundaries is common. By specifying a unique PRIMARY KEY (such as `source_id`), `INSERT OR IGNORE` guarantees that re-running pipelines will only insert brand new listings, seamlessly ignoring duplicates without triggering system runtime exceptions or breaking transaction loops.

### Day 4: The QA Inspector & Orchestrator (Orchestration & DAGs)
Reflections on Failures and Directed Acyclic Graphs (DAGs):
If a manual processing script crashes halfway through a run, the system state becomes partially committed, leading to missing data records or duplicate loading hazards. Fixing this manually requires an engineer to manually check output folders, deduce where the break occurred, fix code bugs, and stitch execution stages back together by hand.

Automated orchestrators (like Apache Airflow) resolve these issues by organizing pipelines into strict Directed Acyclic Graphs (DAGs) where individual stages (Ingest → Process → Load) operate as isolated tasks with explicit dependencies. If the processing step fails, the orchestrator halts execution before touching the database, alerts the team, and allows for isolated retries from the exact point of failure. This structural isolation ensures data lineage remains intact and production databases are never exposed to corrupt states.