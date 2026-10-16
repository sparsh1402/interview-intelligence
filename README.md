# Interview Intelligence

A structured, searchable knowledge base of software engineering interview experiences, questions, solutions and preparation plans, with an interactive dashboard built from it.

Target roles: SDE-1/SDE-2, Java Backend Developer, Software Engineer.

## What's in the repo

```
kb/                          the knowledge base (source of truth)
  README.md                  ID conventions, status vocabularies, changelog
  experiences/EXP-xxxx-*.md  raw interview experiences, verbatim
  data/question_bank.csv     canonical questions (one row per distinct question)
  data/question_appearances.csv  every time a question was asked, with original wording
  companies/<company>.md     company guides
  solutions/<topic>.md       solutions and revision notes, keyed by question ID
  topic_index.md             topic → question IDs
  plans/                     preparation plans
dashboard/
  template.html              dashboard page (HTML/CSS/JS)
  build.py                   turns kb/ into site/index.html (Python 3, standard library only)
.github/workflows/pages.yml  builds and deploys the dashboard to GitHub Pages on every push to main
```

`site/` is generated and git-ignored.

## Dashboard features

- Search across titles, original wording, solutions and your notes
- Filters: company, topic, type, solution status, your progress; sort by most asked or least prepared
- Question detail: metadata, every place it was asked (round + original wording), rendered solution with highlighted Java, your notes
- Progress tracking per question (Not started → Learning → Confident → Mastered), readiness bar, per-topic progress
- Companies: full guide plus raw experiences
- Topics: times asked by topic, coloured by your progress, plus target areas with no data yet
- Rapid-fire drill: timed questions (reported + generated mock), self-rating, optional progress update
- Plans: renders anything in `kb/plans/`
- Deep links: `…/#Q-0022` opens a question; `#companies`, `#topics`, `#drill`, `#plans` open a tab

Progress and notes are stored in your browser (localStorage), not in the repo. Use **Back up progress** to copy them between browsers or between the GitHub Pages site and the Claude artifact.

## Build locally

```bash
python dashboard/build.py
# open site/index.html in a browser
```

## Deploy to GitHub Pages

1. Create a repository and push this folder to the `main` branch.
2. In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Push any change (or run the workflow from the **Actions** tab). The site appears at `https://<your-username>.github.io/<repo-name>/`.

Every later push that touches `kb/` or `dashboard/` rebuilds and redeploys automatically.

**Visibility:** on a free GitHub account, Pages only works for public repositories, so everything in `kb/` (including raw experiences and your notes in the solution files) becomes public. Private-repo Pages needs a paid plan.

## Adding a new interview experience

Paste it to Claude in the "Software Engineering Interview Intelligence" project. Claude updates the files in `kb/`; commit and push them, and the dashboard redeploys.

## Sources

Raw experiences in `kb/experiences/` are other candidates' self-reported accounts. Each file records what is known about its source; unknown authors and URLs are marked Unknown.
