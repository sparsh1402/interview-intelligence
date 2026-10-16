# Interview Intelligence Knowledge Base

Owner: Sparsh Agarwal · Target: SDE-1/SDE-2, Java Backend, Software Engineer (product companies)
Created: 2026-10-16 · Last updated: 2026-10-16

## Folder structure

| Path | What it holds | Rule |
|---|---|---|
| `kb/README.md` | This file: structure, ID conventions, changelog | — |
| `kb/experiences/EXP-xxxx-*.md` | Raw interview experiences, verbatim, with metadata | Never edited after ingestion except metadata corrections |
| `kb/data/question_bank.csv` | Canonical questions — one row per distinct question | Recurring questions reuse the existing ID |
| `kb/data/question_appearances.csv` | Every occurrence of a question (QID × experience × round), with original wording | One row per occurrence; preserves source context |
| `kb/companies/<company>.md` | Company guide (standard 13-section structure) | Facts vs. inferences kept separate |
| `kb/solutions/<topic>.md` | Derived solutions and revision notes, keyed by QID | Derived content, never mixed into raw experiences |
| `kb/topic_index.md` | Topic → question IDs, with dataset frequency | — |
| `kb/plans/` | Preparation plans (none yet) | — |

## ID conventions

- Experience: `EXP-0001`, `EXP-0002`, …
- Canonical question: `Q-0001`, … (shared across companies)
- Appearance (occurrence): `APP-0001`, …
- Solution anchor: the QID heading inside `kb/solutions/<topic>.md`

## Status vocabularies

- **Difficulty**: `Easy | Medium | Hard | Unknown`. `difficulty_reported` comes only from the source; `difficulty_estimated` is my judgement and is labelled as such.
- **Solution status**: `Drafted` (notes written, not reviewed by you) · `Reviewed` (you've studied it) · `Mastered` (you can answer it under time pressure) · `Queued` (not written yet) · `Needs-details` (source too vague to solve exactly) · `Needs-user-input` (depends on your own experience).

## Frequency caveat

All frequency counts are **within this collected dataset only**. They are not evidence of how often a company asks something. With one experience per company, a count of 1 means "reported once", nothing more.

## Changelog

- 2026-10-16 — KB created. Ingested EXP-0001 (Mastercard, SDE 2 Full Stack). Added Q-0001 – Q-0023, APP-0001 – APP-0027, Mastercard guide, 5 solution files, topic index.
- 2026-10-16 — Added dashboard (`dashboard/template.html`, `dashboard/build.py`) and GitHub Pages workflow. Dashboard reads `kb/` at build time; keep CSV headers and `## Q-xxxx` solution headings stable so the build can parse them.
