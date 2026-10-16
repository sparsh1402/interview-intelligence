# Solutions — High-Level Design

Derived content. Status: **Drafted**. Numbers below are **my assumptions** for practice; state your own in the interview and ask the interviewer to confirm them.

---

## Q-0027 — Design a URL shortening service

Asked at Google (EXP-0002, R3). The candidate reports covering hashing strategy, database schema, Redis caching and high read throughput. Below is a full 45-minute answer, in the order to present it.

### 1. Requirements (first 5 minutes — ask, don't assume)

**Functional**
- Create a short link for a long URL; optional custom alias; optional expiry.
- Redirect `GET /{code}` to the long URL.
- Optional: click analytics, delete/disable a link, per-user link list.

**Non-functional**
- Redirects are the hot path: very low latency (aim p99 < 50 ms server-side) and highly available.
- Read-heavy (assume 100 reads : 1 write).
- Short codes must be unique and should not be guessable in sequence (abuse / enumeration).
- Durable: a created link must never point to the wrong URL.

### 2. Capacity estimates (assumptions)

| Quantity | Assumption / calculation | Result |
|---|---|---|
| New links | 100 M / month | ≈ 40 writes/s avg |
| Redirects | 100 × writes | ≈ 4,000 reads/s avg, plan for ~20k/s peak |
| Retention | 5 years × 1.2 B/year | 6 B links |
| Record size | code + URL + metadata ≈ 500 B | ≈ 3 TB total |
| Code length | base62, 7 chars = 62⁷ | ≈ 3.5 trillion codes (plenty for 6 B) |
| Cache | hot links follow a power law; cache the top ~20% of daily accessed links | tens of GB, fits in a Redis cluster |

Say why it matters: writes are tiny, reads dominate, so the design is **cache-first redirects** plus a **collision-free ID scheme**.

### 3. API

```
POST /api/v1/links          { "longUrl": "...", "alias": "optional", "expiresAt": "optional" }
  -> 201 { "code": "aZ3k9Qx", "shortUrl": "https://sho.rt/aZ3k9Qx" }
  -> 409 if alias taken, 400 for invalid/blocked URL
GET  /{code}                -> 302 Location: <longUrl>   (404 if unknown, 410 if expired/disabled)
DELETE /api/v1/links/{code} -> 204 (owner only)
GET  /api/v1/links/{code}/stats -> click counts
```
Add an **idempotency key** header on POST so client retries don't create duplicate links. Authenticate creation (API key / OAuth) and rate-limit per user/IP.

**301 vs 302:** 301 (permanent) is cached by browsers, so fewer hits on you but you lose click analytics and can't change or expire the target. Choose **302** (or 307) if analytics or expiry matter; 301 if pure cost reduction.

### 4. Short-code generation (the core trade-off)

| Approach | How | Pros | Cons |
|---|---|---|---|
| **Hash the URL** (MD5/SHA-256 → base62, take 7 chars) | Deterministic | Same URL → same code (dedupe for free) | Truncation causes **collisions** → check DB and retry with salt; dedupe is wrong if two users want separate links/analytics |
| **Global counter → base62** | DB sequence or Redis `INCR`, encode | No collisions, short codes | Single point of contention; **sequential codes are guessable** (enumeration) |
| **Range allocation (recommended)** | A coordinator (ZooKeeper / DB row) hands each app server a block of IDs (e.g. 1 M); server encodes locally | No per-request coordination, no collisions, scales horizontally | Gaps if a server dies (fine); still sequential within a block → apply a reversible bijective shuffle (e.g. Feistel / multiply by a large odd number mod 62⁷) before base62 |
| **Pre-generated key service (KGS)** | Offline job fills a table of random unused codes; servers fetch batches | Random, non-guessable, fast | Extra service; must mark keys used atomically so two servers never get the same batch |
| **Snowflake-style 64-bit IDs** | timestamp + machine + sequence | Decentralized | 64 bits → ~11 base62 chars, longer codes |

**What to say:** "I'd use range allocation with a bijective scramble: no hot coordinator on the write path, no collision checks, and codes don't reveal order. Custom aliases go through a separate path with a unique-constraint insert."

Base62 encoding in Java:
```java
private static final char[] ALPHABET =
        "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".toCharArray();

static String toBase62(long id) {
    if (id == 0) return "0";
    StringBuilder sb = new StringBuilder();
    while (id > 0) {
        sb.append(ALPHABET[(int) (id % 62)]);
        id /= 62;
    }
    return sb.reverse().toString();
}
```

### 5. Data model

```
links
  code         VARCHAR(10)  PRIMARY KEY      -- partition key
  long_url     TEXT         NOT NULL
  owner_id     BIGINT       NULL
  created_at   TIMESTAMP    NOT NULL
  expires_at   TIMESTAMP    NULL
  status       SMALLINT     NOT NULL         -- active / disabled
```
Optional secondary index `(owner_id, created_at)` for "my links". If you dedupe by URL, add `url_hash` with an index.

**SQL or NoSQL?** The access pattern is a pure key-value lookup by `code` with no joins, so a horizontally scalable KV/wide-column store (Bigtable, Cassandra, DynamoDB) fits naturally. Sharded MySQL/Postgres also works at 3 TB. Mention both and pick one with a reason: "KV store, partitioned by code, replicated across 3 zones."

### 6. Architecture

```
           ┌──────────── CDN / edge (optional, caches 301/302 for hot codes)
Client ──► Load balancer ──► Redirect service (stateless, many replicas)
                                 │  1. Redis cluster (cache-aside, TTL)
                                 │  2. on miss → KV store (replicated, partitioned by code)
                                 │  3. emit click event ──► Kafka ──► analytics consumers ──► OLAP store
                                 ▼
           Write API service ──► ID range allocator (ZooKeeper / DB) ──► KV store
                                 └─► URL safety check (blocklist / malware scan, async)
```
- **Separate read and write services** so redirect capacity scales independently.
- **Analytics is async**: never put a DB write on the redirect path; publish to Kafka and aggregate.

### 7. Scaling the read path (the candidate's "high read throughput" point)

- **Cache-aside in Redis**: `GET code` → hit: redirect; miss: read DB, `SET code url EX 86400`. Hot links get ~99% hit rate.
- **Cache negative results** (unknown codes) briefly, to stop random-code scans from hammering the DB.
- **Hot keys** (one viral link): replicate the key across Redis shards or add a small in-process LRU (Caffeine) in each redirect server.
- **Thundering herd** on a popular key's expiry: request coalescing (single-flight) or jittered TTLs.
- Read replicas / multi-region replicas of the store; route users to the nearest region (latency).

### 8. Reliability, consistency, failure scenarios

| Failure | Effect | Mitigation |
|---|---|---|
| Redis down | All reads hit DB | DB sized for degraded mode; circuit breaker; local LRU |
| DB partition unavailable | Some codes fail | 3-way replication across zones; quorum reads |
| ID allocator down | No new links | Servers hold a pre-fetched range; redirects unaffected |
| App server crashes mid-range | Unused IDs lost | Acceptable gaps |
| Duplicate POST from client retry | Two links | Idempotency key |
| Malicious URLs / spam | Abuse | Safe-browsing check, rate limits, disable status |

**Consistency:** a new link must be readable right after creation. Write to the primary and either read-your-writes from the primary for the creator, or write-through into Redis on create. Redirects can tolerate eventual consistency for analytics counts.

**Expiry:** check `expires_at` on read (lazy), plus a background job to purge; set Redis TTL ≤ expiry.

### 9. Monitoring

Redirect p50/p99 latency, cache hit ratio, 4xx/5xx rates, DB read QPS, ID range remaining per server, Kafka consumer lag, abuse-report rate.

### 10. Likely follow-ups

- *How do you avoid collisions with hashing?* Check-and-retry with a salt, or switch to range IDs; explain the birthday-problem risk when truncating hashes.
- *Make codes non-guessable?* Bijective scramble or random KGS keys; never expose raw sequence numbers.
- *Custom alias race?* Rely on the primary-key unique constraint and return 409 on conflict.
- *Global deployment?* Region-local caches and replicas; ID ranges per region so regions never collide.
- *How would you support 1 M redirects/s?* CDN/edge caching of redirects, more Redis shards, local caches; the DB stays mostly cold.

**Interview technique:** spend ~5 min on requirements and numbers, ~10 min on API + ID generation, ~15 min on architecture and the read path, ~10 min on failures and trade-offs, and leave time for questions. Drive the conversation; check in with the interviewer at each stage.

**Related practice:** design Pastebin, a rate limiter, a key-value store, a unique ID generator, TinyURL with analytics dashboard.
