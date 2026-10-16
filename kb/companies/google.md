# Google — Company Interview Guide

Last updated: 2026-10-16 · Experiences in dataset: **1** (EXP-0002)

> **Evidence level: LOW.** "Reported" content comes from one candidate's self-reported account. Sections marked **[Inference]** or **[General advice]** are mine, not from the source.

## 1. Company overview and target roles

- Roles seen in dataset: Software Engineer (SDE-2), Bangalore — EXP-0002. Candidate had 4 years of experience.
- Relevance to you: same level you're targeting. The reported rounds are language-agnostic DSA + system design + behavioral; no Java/Spring questions were reported.

## 2. Interview experiences and source references

| ID | Role | Date | Location | Format | Outcome | Source |
|---|---|---|---|---|---|---|
| EXP-0002 | SDE-2 | Jan 15, 2025 (reported) | Bangalore | Phone screen + on-site (reported 5 rounds, 4 described) | Unknown | Text file attached by user, 2026-10-16; author/URL unknown |

## 3. Hiring process and reported rounds

**Reported (EXP-0002):** about 3 weeks from recruiter call to decision.

| Round | Type | Duration | Medium |
|---|---|---|---|
| R1 | Phone screen — DSA | 45 min | Google Meet + shared Google Doc (no IDE) |
| R2 | On-site technical 1 — trees & graphs | 45 min | In person, Google Bangalore |
| R3 | System design | 45 min | Unknown |
| R4 | Behavioral | 30 min | Unknown |
| ? | **Missing round** | — | The candidate says there were 3 technical on-site rounds, but only 2 (R2, R3) are described |

Not reported: online assessment, team matching, hiring committee, offer details, outcome.

## 4. Round-by-round questions

- **R1:** Q-0031 background (brief) · Q-0024 unique pairs summing to target in a sorted array (follow-up: duplicates)
- **R2:** Q-0025 LCA in a binary tree · Q-0026 LCA in a BST (follow-up)
- **R3:** Q-0027 design a URL shortener
- **R4:** Q-0028 disagreements · Q-0029 decisions with incomplete information · Q-0030 mentoring juniors

## 5. DSA and coding problems

| QID | Problem | Est. difficulty | Java solution |
|---|---|---|---|
| Q-0024 | Unique pairs with target sum (sorted) | Easy | `solutions/dsa.md#Q-0024` |
| Q-0025 | LCA of binary tree | Medium | `solutions/dsa.md#Q-0025` |
| Q-0026 | LCA of BST | Easy | `solutions/dsa.md#Q-0026` |

The candidate coded in Python; all KB solutions are in Java. Coding was done in a **Google Doc without autocomplete** (reported).

## 6. Core CS and language questions

None reported.

## 7. LLD and HLD questions

- Q-0027 URL shortener (HLD) → `solutions/hld.md`. Candidate covered hashing, schema, Redis caching and read throughput (reported); outcome of that round unknown.

## 8. Behavioral and managerial questions

Q-0028, Q-0029, Q-0030, Q-0031 → `solutions/behavioral.md`. **Needs your real stories.**

## 9. Solutions and revision notes

`solutions/dsa.md` (Q-0024 – Q-0026), `solutions/hld.md` (Q-0027), `solutions/behavioral.md` (Q-0028 – Q-0031).

## 10. Frequently recurring topics (n = 1 experience)

Trees (2 questions), arrays/two pointers (1), HLD (1), behavioral (4 incl. intro). No topic recurs yet; nothing here supports frequency claims.

The candidate's own tips (reported): practise coding in a Google Doc, narrate your thinking, study graphs / DP / trees, practise scalable system design, prepare STAR stories. Note: **graphs and DP were recommended but not asked** in the described rounds.

## 11. Preparation roadmap

**[Inference from EXP-0002]**
1. Easy/medium DSA in Java without an IDE: arrays & two pointers, trees (LCA family, BST properties).
2. One HLD problem end-to-end in 45 minutes (URL shortener first, since it was asked).
3. 4–5 STAR stories covering conflict, ambiguity and mentoring.

**[General advice — not from evidence]:** Google interviews are widely described as DSA-heavy with graphs and dynamic programming common at SDE-2; the candidate's tip agrees. Add BFS/DFS, topological sort, Dijkstra, union-find and 1-D/2-D DP to your plan. Don't over-weight Java framework questions for Google.

## 12. Mock interview questions [Generated — not reported]

1. Return the count of pairs (by index, duplicates included) summing to target in a sorted array.
2. Same problem, but the array is unsorted and doesn't fit in memory.
3. 3Sum: all unique triplets summing to zero.
4. LCA when p or q might not be in the tree.
5. LCA when each node has a parent pointer, in O(1) extra space.
6. Distance between two nodes in a binary tree.
7. URL shortener: how do you make codes non-guessable without collision checks?
8. URL shortener: a single link goes viral at 500k redirects/s. What breaks first?
9. URL shortener: 301 or 302, and why?
10. Tell me about a time you disagreed with a senior engineer's design.
11. Tell me about a production decision you made without full data.
12. How did you help a junior engineer become independent?

## 13. Unresolved questions and evidence gaps

- The missing third technical on-site round (topic unknown).
- Outcome of the process; per-round feedback.
- Whether Jan 15, 2025 is the date of one round or the whole loop.
- Source author / platform / URL.
- Whether candidate-reported complexity and correctness were challenged (only "satisfied" is reported for R1).
- Need more independent Google SDE-2 experiences (2025–2026, India) before trusting any pattern.
