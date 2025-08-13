"""Download a few permissively available HR/IT policy web pages and build qa_dataset.json.
This is a lightweight demo builder that scrapes public pages and generates simple Q/A pairs.

Run:
  python scripts/build_demo_dataset.py
Outputs:
  backend/app/data/qa_dataset.json
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


SOURCES = [
    # Public university HR/IT policies (for demo; replace with your org sources when available)
    "https://policy.umn.edu/hr/leave",
    "https://hr.berkeley.edu/policies",
    "https://www.washington.edu/admin/rules/policies/APS/APS45.01.html",
]


def fetch_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        if url.lower().endswith(".pdf"):
            # For simplicity: record a placeholder; PDF parsing is out of scope here
            return "PDF policy document from: " + url
        soup = BeautifulSoup(r.text, "lxml")
        for s in soup(["script", "style", "nav", "footer", "header"]):
            s.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text[:8000]
    except Exception as e:
        return f"Failed to fetch {url}: {e}"


def make_qa(text: str, url: str) -> list[dict]:
    host = urlparse(url).netloc
    return [
        {
            "question": f"Where can I read leave policy details (source: {host})?",
            "answer": f"Refer to: {url}. Summary excerpt: " + text[:300],
        },
        {
            "question": f"What policies are listed at {host}?",
            "answer": f"The page enumerates policies and guidance. See: {url}",
        },
    ]


def main() -> None:
    qa: list[dict] = []
    for url in SOURCES:
        text = fetch_text(url)
        if text.startswith("Failed to fetch"):
            print(text)
            continue
        qa.extend(make_qa(text, url))

    out = Path(__file__).resolve().parents[1] / "backend" / "app" / "data" / "qa_dataset.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(qa, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(qa)} Q/A items to {out}")


if __name__ == "__main__":
    main()


