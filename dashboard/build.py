#!/usr/bin/env python3
"""Build the interview-prep dashboard from the kb/ folder.

Usage:  python dashboard/build.py
Output: site/index.html   (full HTML page for GitHub Pages)
        site/artifact.html (same page without the document skeleton, for claude.ai Artifacts)

Standard library only. Re-run after adding experiences, questions, solutions or plans.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "kb"
TEMPLATE = Path(__file__).resolve().parent / "template.html"
OUT = ROOT / "site"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Very small YAML-ish frontmatter parser: `key: value` lines only."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, text[end + 4:].lstrip("\n")


def slug(heading: str) -> str:
    s = heading.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "-", s.strip())


def h2_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) pairs at level-2 headings."""
    parts = re.split(r"(?m)^## (.+)$", text)
    out = []
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1].strip()))
    return out


def find_section(md_text: str, anchor: str) -> str | None:
    for heading, body in h2_sections(md_text):
        if anchor.startswith("Q-") and heading.startswith(anchor):
            return f"## {heading}\n\n{body}"
        if not anchor.startswith("Q-") and anchor.lower() in slug(heading):
            return f"## {heading}\n\n{body}"
    return None


def main() -> None:
    questions = read_csv(KB / "data" / "question_bank.csv")
    appearances = read_csv(KB / "data" / "question_appearances.csv")

    experiences = []
    for p in sorted((KB / "experiences").glob("*.md")):
        meta, body = split_frontmatter(read(p))
        experiences.append({"id": meta.get("id", p.stem), "file": p.name, "meta": meta, "body": body})

    companies = []
    for p in sorted((KB / "companies").glob("*.md")):
        text = read(p)
        mocks = []
        for heading, body in h2_sections(text):
            if "mock interview" in heading.lower():
                mocks = [m.group(1).strip() for m in re.finditer(r"(?m)^\d+\.\s+(.+)$", body)]
        title = re.search(r"(?m)^# (.+)$", text)
        name = title.group(1).split("—")[0].strip() if title else p.stem.title()
        companies.append({"slug": p.stem, "name": name, "md": text, "mocks": mocks})

    plans = []
    plans_dir = KB / "plans"
    if plans_dir.exists():
        for p in sorted(plans_dir.glob("*.md")):
            text = read(p)
            title = re.search(r"(?m)^# (.+)$", text)
            plans.append({"file": p.name, "title": title.group(1) if title else p.stem, "md": text})

    md_cache: dict[str, str] = {}
    for q in questions:
        ref = q.get("solution_ref", "")
        q["solution_md"] = ""
        if "#" in ref:
            file_part, anchor = ref.split("#", 1)
            path = KB / file_part
            if path.exists():
                md_cache.setdefault(file_part, read(path))
                q["solution_md"] = find_section(md_cache[file_part], anchor) or ""
        q["appearances"] = [a for a in appearances if a["qid"] == q["qid"]]

    data = {
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "questions": questions,
        "experiences": experiences,
        "companies": companies,
        "plans": plans,
    }

    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = read(TEMPLATE).replace("__KB_DATA__", payload)

    OUT.mkdir(exist_ok=True)
    (OUT / "artifact.html").write_text(page, encoding="utf-8")
    full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
            'body{margin:0}[hidden]{display:none!important}*,*::before,*::after{box-sizing:border-box}</style>\n'
            '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
    (OUT / "index.html").write_text(full, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Built site/ with {len(questions)} questions, {len(appearances)} appearances, "
          f"{len(experiences)} experiences, {len(companies)} companies, {len(plans)} plans.")


if __name__ == "__main__":
    main()
