"""Build org-specific QA dataset from PDFs/DOCX/TXT under org_data.

Scans org_data/policies and org_data/it_policies, parses text, summarizes,
and produces backend/app/data/qa_dataset.json so the chatbot answers your
organization's content.

Run:
  python scripts/build_qa_from_org_policies.py
"""
from __future__ import annotations

import json
from pathlib import Path

import sys
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.services.doc_parser import parse_document
from backend.app.services.summarizer import Summarizer


def collect_files(base: Path) -> list[Path]:
    files: list[Path] = []
    for ext in (".pdf", ".docx", ".txt"):
        files.extend(base.rglob(f"*{ext}"))
    return files


def make_qas_for_file(path: Path, text: str, summarizer: Summarizer) -> list[dict]:
    title = path.stem.replace("_", " ").title()
    summary = summarizer.summarize(text)
    qas = [
        {
            "question": f"What does the {title} describe?",
            "answer": summary,
        },
        {
            "question": f"Where can I read the {title}?",
            "answer": f"See internal policy document: {path.as_posix()}",
        },
    ]
    return qas


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    org_root = project_root / "org_data"
    policies_dir = org_root / "policies"
    it_policies_dir = org_root / "it_policies"

    files = []
    if policies_dir.exists():
        files += collect_files(policies_dir)
    if it_policies_dir.exists():
        files += collect_files(it_policies_dir)

    if not files:
        print("No policy files found under org_data. Run scripts/generate_org_policies.py or add your documents.")
        return

    summarizer = Summarizer()
    qa: list[dict] = []

    for p in files:
        try:
            text = parse_document(p.name, p.read_bytes())
            qa.extend(make_qas_for_file(p, text, summarizer))
            print(f"Indexed: {p}")
        except Exception as e:
            print(f"Failed to index {p}: {e}")

    out = project_root / "backend" / "app" / "data" / "qa_dataset.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(qa, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(qa)} Q/A items to {out}")


if __name__ == "__main__":
    main()


