"""
Auto Log Cleaner — keeps LGP tidy by archiving old diagnostic reports.
"""

from datetime import datetime
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
LGP = BASE_DIR / "lgp.txt"
ARCHIVE = BASE_DIR / "archive"
HEADER = "=== StudioCore — FULL SYSTEM DIAGNOSTIC REPORT ==="


def archive_reports(reports: list[str]) -> Path:
    """Archive the provided reports and return the archive file path."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    archive_path = ARCHIVE / f"lgp_archive_{timestamp}.txt"
    archive_body = "".join(f"{HEADER}{report}" for report in reports)
    archive_path.write_text(archive_body, encoding="utf-8")
    return archive_path


def main() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    if not LGP.exists():
        print("LGP file not found; nothing to clean.")
        return

    text = LGP.read_text(encoding="utf-8")
    chunks = re.split(rf"{re.escape(HEADER)}", text)
    header_prefix = chunks[0]
    reports = chunks[1:]

    if len(reports) <= 30:
        print("No archiving needed; 30 or fewer reports present.")
        return

    old_reports = reports[:-30]
    archive_path = archive_reports(old_reports)

    new_content = header_prefix + "".join(f"{HEADER}{report}" for report in reports[-30:])
    LGP.write_text(new_content, encoding="utf-8")

    print(f"Archived {len(old_reports)} reports to {archive_path.name} and kept the latest 30.")


if __name__ == "__main__":
    main()
