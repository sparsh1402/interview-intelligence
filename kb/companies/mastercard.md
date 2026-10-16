# Mastercard — Company Interview Guide

Last updated: 2026-10-16 · Experiences in dataset: **1** (EXP-0001)

> **Evidence level: LOW.** Everything under "Reported" comes from one candidate's self-reported account. It is not proof of Mastercard's standard process. Sections marked **[Inference]** or **[General advice]** are mine.

## 1. Company overview and target roles

- Roles seen in dataset: SDE 2 — Full Stack Developer (Angular + Spring Boot backend) — EXP-0001.
- Relevance to you: Java/Spring Boot backend focus matches your stack. The Angular side was **not** examined in the reported rounds.

## 2. Interview experiences and source references

| ID | Role | Date | Location | Format | Outcome | Source |
|---|---|---|---|---|---|---|
| EXP-0001 | SDE 2 Full Stack | Unknown | Unknown | Super Day, 3 × 45 min back-to-back | Rejected | Text pasted by user, 2026-10-16; original author/URL unknown |

## 3. Hiring process and reported rounds

**Reported (EXP-0001):**
| Round | Type | Interviewer | Duration | Reported difficulty |
|---|---|---|---|---|
| R1 | Core Java & fundamentals (theory) | Unknown | 45 min | "moderate" |
| R2 | Spring + concurrency deep dive, rapid-fire | Senior developer | 45 min | "intense"; ~new question every 10 seconds |
| R3 | Managerial + DSA | Unknown (likely manager — inferred from round name) | 45 min | DSA "moderate/easy" |

Not reported: online assessment, recruiter/HR round, system design (HLD) round, Angular/front-end round, offer/negotiation steps.

## 4. Round-by-round questions

- **R1:** Q-0001 memory management · Q-0002 string pool · Q-0003 Java 8 features · Q-0004 multithreading vs multitasking · Q-0005 executor services/thread pools · Q-0006 SOLID · Q-0007 OO design
- **R2:** Q-0008 Spring Boot annotations · Q-0009 Spring vs Spring Boot 3 · Q-0010 Spring Security · Q-0011 JPA/Hibernate · Q-0012 `@Autowired` vs constructor injection · Q-0005 executor services (detailed) · Q-0013 old vs new Java features · Q-0001 memory handling · Q-0014 GC · Q-0015 lock types · Q-0016 lock placement scenarios · Q-0017 project deep dive · Q-0018 justify "30% query improvement" · Q-0019 design patterns
- **R3:** Q-0020 DSA (HashMap + sorting) · Q-0021 thread pool creation · Q-0022 do threads actually die · Q-0023 thread lifecycle · Q-0005 executors (again) · Q-0004 multithreading (revisited)

Full wording: `data/question_appearances.csv`.

## 5. DSA and coding problems

- Q-0020 — HashMap + sorting, easy/medium. **Exact problem unknown.** Practice proxy in `solutions/dsa.md`.
- No live-coding of concurrency code was reported, but R2's lock-placement scenarios may have needed it.

## 6. Core CS and language questions

Java core: Q-0001, Q-0002, Q-0003, Q-0013, Q-0014 → `solutions/java-core.md`
Concurrency: Q-0004, Q-0005, Q-0015, Q-0016, Q-0021, Q-0022, Q-0023 → `solutions/concurrency.md`
Spring: Q-0008 – Q-0012 → `solutions/spring.md`
Not reported: DBMS/SQL theory, OS, networks. (JPA was asked; SQL tuning is implied by Q-0018.)

## 7. LLD and HLD questions

- SOLID (Q-0006), OOD (Q-0007), design patterns (Q-0019) → `solutions/design.md`
- No full LLD or HLD problem was reported. The candidate's takeaway mentions "system design principles & patterns" but the body describes only patterns/SOLID. **Treat HLD at Mastercard as unknown.**

## 8. Behavioral and managerial questions

**Q-0017 / Q-0018 — project deep dive & metric justification. Status: Needs-user-input.**

What the interviewer was testing **[Inference]**: whether a resume number is *measured* or *made up*. "Why 30% and not 25%?" has only one good answer: "Because that's what we measured, here's how."

Answer framework for any metric on your resume:
1. **Baseline** — what was measured (p50/p95 latency? throughput? DB time?), on what data volume, environment, how many runs.
2. **Root cause** — how you found it (EXPLAIN plan, slow query log, Hibernate statistics, APM traces, N+1 detection).
3. **Change** — index, query rewrite, fetch join, pagination, caching, batching.
4. **Result calculation** — `(before − after) / before`. E.g. p95 from 800 ms → 560 ms = 30%. Say which percentile and why.
5. **Caveats** — "measured in staging with production-like data; in production we saw a similar drop in the APM dashboard." Honesty about uncertainty scores better than false precision.
6. **Business impact** — what that latency/throughput change meant for users or cost.

Action for you: list every number on your resume and fill this template for each. I need your real project details — I won't invent them.

## 9. Solutions and revision notes

| File | Questions |
|---|---|
| `solutions/concurrency.md` | Q-0004, Q-0005, Q-0015, Q-0016, Q-0021, Q-0022, Q-0023 |
| `solutions/java-core.md` | Q-0001, Q-0002, Q-0003, Q-0013, Q-0014 |
| `solutions/spring.md` | Q-0008 – Q-0012 |
| `solutions/design.md` | Q-0006, Q-0007, Q-0019 |
| `solutions/dsa.md` | Q-0020 (proxy) |

## 10. Frequently recurring topics (dataset counts, n = 1 experience)

| Topic | Appearances in EXP-0001 | Note |
|---|---|---|
| Executor services / thread pools | **3 rounds** (Q-0005) + Q-0021, Q-0022, Q-0023 | Strongest signal — recurred *within* one Super Day |
| Multithreading / concurrency | R1, R2, R3 | Includes locks and scenarios |
| Java memory / GC | R1, R2 | |
| Spring ecosystem | R2 (5 questions) | |
| Project metrics | R2 | Candidate's suspected failure point |

Recurrence within a single candidate's Super Day suggests interviewers either shared notes or probed a perceived weakness **[Inference]** — it is not evidence of company-wide frequency.

## 11. Preparation roadmap

Priorities **[Inference from EXP-0001]**:
1. Concurrency + executors to *internals* depth (submission algorithm, worker lifecycle, lock choice and placement).
2. Every resume metric defensible (Q-0018 framework).
3. Spring Boot 3 / Security 6 / JPA performance (N+1, transactions, proxies).
4. JVM memory + GC.
5. Rapid-fire delivery: 20–30 second crisp answers, then expand only if asked.
6. Easy/medium HashMap + sorting DSA.

**[General advice — not from evidence]:** Mastercard is a payments company; concurrency correctness across instances (DB locking, idempotency, double-spend prevention) is a natural follow-up area. Also prepare basic Angular/full-stack questions for a Full Stack title even though none were reported.

No dated plan yet — ask for a 3/7/14-day plan with your interview date.

## 12. Mock interview questions [Generated — not reported]

Rapid-fire set modelled on R2's style (answer each in ≤ 30 s):
1. What happens when you submit a task to a `ThreadPoolExecutor` whose core threads are all busy?
2. Why is `maximumPoolSize` ignored with a `LinkedBlockingQueue()`?
3. Your task throws a `RuntimeException` inside `submit()`. Where does it go?
4. A thread in a fixed pool finishes its task. What state is it in now?
5. `synchronized` vs `ReentrantLock` — give one case where you *must* use `ReentrantLock`.
6. Two users transfer money A→B and B→A simultaneously. Where's the deadlock and how do you fix it?
7. Your service runs on 3 pods. Does `synchronized` protect the balance update?
8. `@Transactional` method calls another `@Transactional(REQUIRES_NEW)` method in the same class. What happens?
9. What's the N+1 problem and how did you fix it in your project?
10. What changed from `javax` to `jakarta` and why did it matter for Boot 3 migration?
11. How does `SecurityFilterChain` replace `WebSecurityConfigurerAdapter`?
12. Why constructor injection? Give two concrete benefits.
13. `"a" + "b" == "ab"` — true or false, and why?
14. Where does the string pool live since Java 7?
15. Name the G1 default pause target and when you'd switch to ZGC.
16. Which design pattern is Spring AOP built on? Where else is Chain of Responsibility used in Spring?
17. You claimed "30% faster queries". Walk me through the measurement.

## 13. Unresolved questions and evidence gaps

- Exact DSA problem (Q-0020).
- Exact lock-placement scenarios (Q-0016) and Spring Security/JPA sub-questions.
- Interview date, location, candidate's years of experience, source platform/URL.
- Whether any Angular/front-end or HLD round exists for this role.
- Whether rejection was due to R2 — candidate's speculation only.
- Only one experience: need 2–3 more independent Mastercard experiences (ideally 2025–2026, SDE 2, Pune/India) before trusting any pattern.
