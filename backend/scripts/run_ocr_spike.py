"""C4 go/no-go spike harness.

Run this manually once a real GEMINI_API_KEY is configured (GEMINI_MOCK_MODE
must be false) and you have assembled 5-10 representative sample documents,
per the task breakdown:
    - clean English
    - clean Kannada
    - code-mixed Kannada/English
    - at least 2 poor-quality/low-resolution scans

Usage:
    python scripts/run_ocr_spike.py --samples-dir ./ocr_samples

Expected directory layout under --samples-dir:
    ocr_samples/
        clean_english.pdf
        clean_english.reference.txt
        clean_kannada.jpg
        clean_kannada.reference.txt
        code_mixed.jpg
        code_mixed.reference.txt
        low_quality_1.jpg
        low_quality_1.reference.txt
        low_quality_2.jpg
        low_quality_2.reference.txt

For each sample file (any of SUPPORTED_MIME_TYPES) with a matching
`<name>.reference.txt` human transcription, this script:
    1. Sends the file through app.ingestion.ingest_document (the real C4/C7
       Gemini-native path).
    2. Computes a rough character-level similarity ratio against the
       reference transcription (difflib — a cheap proxy for accuracy, good
       enough for a go/no-go call, not a rigorous OCR benchmark).
    3. Prints a per-document accuracy line and appends a row to
       backend/docs/c4_ocr_spike_log.md.

This script has NOT been run against real documents in this environment (no
API key, no sample corpus available here) — it is provided so the team can
run the actual spike themselves before relying on the ingestion pipeline.
"""
from __future__ import annotations

import argparse
import difflib
import mimetypes
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingestion import SUPPORTED_MIME_TYPES, ingest_document  # noqa: E402


def guess_mime(path: Path) -> str | None:
    mime, _ = mimetypes.guess_type(str(path))
    return mime


def run_spike(samples_dir: Path) -> list[dict]:
    results = []
    for sample_path in sorted(samples_dir.iterdir()):
        if sample_path.name.endswith(".reference.txt"):
            continue
        mime = guess_mime(sample_path)
        if mime not in SUPPORTED_MIME_TYPES:
            continue
        reference_path = sample_path.with_suffix("")
        reference_path = sample_path.parent / f"{sample_path.stem}.reference.txt"
        reference_text = (
            reference_path.read_text(encoding="utf-8") if reference_path.exists() else None
        )

        file_bytes = sample_path.read_bytes()
        ingestion_result = ingest_document(file_bytes=file_bytes, content_type=mime)

        accuracy = None
        if reference_text is not None:
            accuracy = difflib.SequenceMatcher(
                None, ingestion_result.extracted_text, reference_text
            ).ratio()

        results.append(
            {
                "file": sample_path.name,
                "mock": ingestion_result.mock,
                "model": ingestion_result.model_used,
                "accuracy_ratio": accuracy,
                "extracted_chars": len(ingestion_result.extracted_text),
            }
        )
        print(
            f"{sample_path.name}: mock={ingestion_result.mock} "
            f"accuracy_ratio={accuracy} extracted_chars={len(ingestion_result.extracted_text)}"
        )
    return results


def append_log(results: list[dict], log_path: Path) -> None:
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## Spike run — {datetime.now(timezone.utc).isoformat()}\n\n")
        f.write("| File | Mock? | Model | Accuracy ratio | Extracted chars |\n")
        f.write("|------|-------|-------|-----------------|------------------|\n")
        for r in results:
            f.write(
                f"| {r['file']} | {r['mock']} | {r['model']} | "
                f"{r['accuracy_ratio']} | {r['extracted_chars']} |\n"
            )
        f.write(
            "\n**Go/no-go decision:** _fill in manually after reviewing the "
            "accuracy ratios and failure modes above — do not auto-decide._\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="C4 OCR go/no-go spike runner")
    parser.add_argument("--samples-dir", required=True, type=Path)
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "docs" / "c4_ocr_spike_log.md",
    )
    args = parser.parse_args()
    spike_results = run_spike(args.samples_dir)
    append_log(spike_results, args.log_path)
    print(f"Appended results to {args.log_path}")
