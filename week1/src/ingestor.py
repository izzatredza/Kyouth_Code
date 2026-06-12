from email import message_from_file
from pathlib import Path
import quopri


def ingest_all_mhtml(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    files = list(input_path.glob("*.mhtml"))

    total = len(files)
    extracted = 0
    failed = 0

    print("🥉 Bronze...")

    if not input_path.exists():
        print(f"❌ Error: Source directory '{input_dir}' does not exist.")
        print("📊 Bronze Summary: Total: 0 | Extracted: 0 | Failed: 0")
        return

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                msg = message_from_file(f)

            html_content = None

            # Find text/html section
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload()

                    html_content = quopri.decodestring(payload).decode(
                        "utf-8", errors="ignore"
                    )

                    break

            if html_content is None:
                print(f"⚠ No HTML content found in: {file.name}")
                failed += 1
                continue

            output_file = output_path / f"{file.stem}.html"

            with open(output_file, "w", encoding="utf-8") as out:
                out.write(html_content)

            print(f"✅ Extracted: {output_file.name}")
            extracted += 1

        except Exception as e:
            print(f"⚠️ No HTML content found in {file.name}: {e}")
            failed += 1

    print("\n📊 Bronze Summary:")
    print(f"Total: {total} | Extracted: {extracted} | Failed: {failed}")
