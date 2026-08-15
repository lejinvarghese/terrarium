#!/usr/bin/env python3
"""Import existing PDFs from archive_data/uploads as sources in Open Notebook."""

import sys
from pathlib import Path

import httpx

ARCHIVE_DATA_DIR = Path(__file__).parent.parent / "data" / "archive_data" / "uploads"
API_BASE_URL = "http://localhost:5055"


def get_existing_sources():
    """Get list of existing sources to avoid duplicates."""
    try:
        response = httpx.get(f"{API_BASE_URL}/api/sources", timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️  Failed to fetch existing sources: {e}")
        return []


def import_pdf(pdf_path: Path):
    """Import a single PDF as a source."""
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            data = {
                "type": "upload",
            }

            response = httpx.post(
                f"{API_BASE_URL}/api/sources",
                files=files,
                data=data,
                timeout=60.0,
            )

            if response.status_code != 200:
                print(f"  ❌ {pdf_path.name}: HTTP {response.status_code}")
                print(f"     Response: {response.text[:200]}")
                return False

            result = response.json()
            print(f"  ✅ {pdf_path.name} → {result.get('id', 'unknown')}")
            return True
    except Exception as e:
        print(f"  ❌ {pdf_path.name}: {e}")
        return False


def main():
    """Main import function."""
    if not ARCHIVE_DATA_DIR.exists():
        print(f"❌ Directory not found: {ARCHIVE_DATA_DIR}")
        sys.exit(1)

    # Find all PDFs
    pdf_files = sorted(ARCHIVE_DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in archive_data/uploads/")
        return

    print(f"📚 Found {len(pdf_files)} PDF files")
    print(f"🔄 Importing to {API_BASE_URL}...\n")

    # Get existing sources to check for duplicates
    existing = get_existing_sources()
    existing_names = {s.get("name", "") for s in existing}

    # Import each PDF
    imported = 0
    skipped = 0
    failed = 0

    for pdf_path in pdf_files:
        name = pdf_path.stem
        if name in existing_names:
            print(f"  ⏭️  {pdf_path.name} (already exists)")
            skipped += 1
        else:
            if import_pdf(pdf_path):
                imported += 1
            else:
                failed += 1

    print("\n✨ Import complete:")
    print(f"  • Imported: {imported}")
    print(f"  • Skipped: {skipped}")
    print(f"  • Failed: {failed}")


if __name__ == "__main__":
    main()
