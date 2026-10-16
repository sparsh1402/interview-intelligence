# Solutions — Concurrency & Thread Pools

Derived content (my explanations), not source material. Status: **Drafted** for all. Java 17+ unless noted; Java 21 notes flagged.

Why this file matters: in EXP-0001 (Mastercard) executor services / thread pools came up in **all three rounds** (dataset frequency 3), and lock placement was the scenario part of the round the candidate thinks sank them.

---

## Q-0004 — Multithreading vs multitasking; multithreading fundamentals

**30-second answer.** Multitasking is the OS running multiple *processes* concurrently; each process has its own address space, so switching is expensive and communication needs IPC. Multithreading is multiple *threads inside one process* sharing heap memory but each with its own stack and program counter; switching is cheaper and communication is just shared memory — which is exactly why you need synchronization.

| | Multitasking (process-based) | Multithreading (thread-based) |
|---|---|---|
| Unit | Process | Thread |
| Memory | Separate address spaces | Shared heap, separate stacks |
| Context switch | Heavy (page tables, TLB flush) | Lighter |
| Communication | IPC (pipes, sockets, shared mem) | Shared objects |
| Failure isolation | Crash stays in one process | One thread can corrupt shared state / bring down JVM (e.g. OOM) |

**Concepts they "revisit in detail" (be ready):**
- **Concurrency vs parallelism** — concurrency is dealing with many things at once (interleaving), parallelism is doing many at once (multiple cores).
- **Three problems of shared state**: *atomicity* (`count++` is read-modify-write), *visibility* (a write in one thread's cache may not be seen by another — fixed by `volatile`/locks via the happens-before rule), *ordering* (compiler/CPU reordering).
- **Race condition, deadlock, livelock, starvation** — define each with one example.
- **Ways to create a thread**: extend `Thread`, implement `Runnable`, `Callable` + `Future`, executors, `CompletableFuture`, virtual threads (21).
- `Runnable` vs `Callable`: `Callable` returns a value and can throw checked exceptions.
- `start()` vs `run()`: `run()` directly executes on the *current* thread — no new thread.

**Common mistake:** saying `volatile` makes `count++` thread-safe. It gives visibility, not atomicity — use `AtomicInteger` / `LongAdder` or a lock.

---

## Q-0005 — ExecutorService: features and usage

**Concept.** `ExecutorService` decouples *task submission* from *how/where tasks run*. Instead of `new Thread()` per task (expensive, unbounded), you hand tasks to a pool that reuses a fixed set of worker threads and queues the overflow.

**Feature list to rattle off:**
- `execute(Runnable)` — fire and forget, no result.
- `submit(Runnable | Callable)` → `Future` (`get()`, `get(timeout)`, `cancel()`, `isDone()`).
- `invokeAll(tasks)` — wait for all; `invokeAny(tasks)` — first successful result, cancel the rest.
- Lifecycle: `shutdown()` (no new tasks, finish queued), `shutdownNow()` (interrupt running, return queued), `awaitTermination(timeout)`, `isShutdown()`, `isTerminated()`.
- `ScheduledExecutorService`: `schedule`, `scheduleAtFixedRate` (fixed start interval), `scheduleWithFixedDelay` (fixed gap after completion).
- `CompletableFuture.supplyAsync(task, executor)` for composition (`thenApply`, `thenCompose`, `thenCombine`, `exceptionally`, `allOf`).

**`Executors` factory methods — and why seniors avoid them in production:**

| Factory | Underlying config | Risk |
|---|---|---|
| `newFixedThreadPool(n)` | core = max = n, **unbounded** `LinkedBlockingQueue` | Queue grows without limit → OOM under load |
| `newSingleThreadExecutor()` | 1 thread, unbounded queue | Same |
| `newCachedThreadPool()` | core 0, max `Integer.MAX_VALUE`, `SynchronousQueue`, 60s keep-alive | Unbounded **threads** under burst → OOM / thrashing |
| `newScheduledThreadPool(n)` | delayed work queue (unbounded) | Same queue risk |
| `newVirtualThreadPerTaskExecutor()` (21) | new virtual thread per task, no pooling | Fine for I/O-bound; bound concurrency with a `Semaphore` if a downstream is limited |

**Production-style pool:**
```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
        8,                                   // corePoolSize
        16,                                  // maximumPoolSize
        30, TimeUnit.SECONDS,                // keepAlive for non-core threads
        new ArrayBlockingQueue<>(500),       // BOUNDED queue -> back-pressure
        new ThreadFactoryBuilderLike("payment-worker-"), // named threads help in thread dumps
        new ThreadPoolExecutor.CallerRunsPolicy());      // overload -> slow the producer down

// Simple named factory without Guava:
final class ThreadFactoryBuilderLike implements ThreadFactory {
    private final String prefix; private final AtomicInteger n = new AtomicInteger();
    ThreadFactoryBuilderLike(String prefix) { this.prefix = prefix; }
    public Thread newThread(Runnable r) { Thread t = new Thread(r, prefix + n.incrementAndGet()); t.setDaemon(false); return t; }
}
```

**Graceful shutdown (frequently asked):**
```java
pool.shutdown();
try {
    if (!pool.awaitTermination(30, TimeUnit.SECONDS)) {
        pool.shutdownNow();                      // interrupts workers
    }
} catch (InterruptedException e) {
    pool.shutdownNow();
    Thread.currentThread().interrupt();          // restore interrupt flag
}
```

**Classic follow-ups:**
- *`execute` vs `submit` with exceptions?* `execute`: exception propagates to the worker → `UncaughtExceptionHandler`, worker thread dies and is replaced. `submit`: exception is captured inside the `Future`; you only see it on `get()` (as `ExecutionException`). Unchecked `Future`s = silently swallowed errors.
- *How do you size a pool?* CPU-bound ≈ number of cores (`Runtime.getRuntime().availableProcessors()`, maybe +1). I/O-bound ≈ cores × (1 + wait time / compute time). Then **measure** — this is a heuristic, not a law.
- *Spring?* `@Async` + a `ThreadPoolTaskExecutor` bean; by default Boot auto-configures one — say you'd configure it explicitly with a bounded queue. Mention `SecurityContext`/MDC don't propagate to pool threads automatically (`DelegatingSecurityContextExecutor`, `TaskDecorator`).
- *Parallel streams?* use the shared `ForkJoinPool.commonPool()` — blocking I/O in a parallel stream starves every other user of the common pool.

---

## Q-0021 — How are thread pools created? (ThreadPoolExecutor internals)

**The 7 constructor parameters:** `corePoolSize`, `maximumPoolSize`, `keepAliveTime` + `unit`, `workQueue`, `threadFactory`, `RejectedExecutionHandler`.

**Submission algorithm (memorize the order — this is the "aha" interviewers look for):**
1. If running threads < `corePoolSize` → create a **new worker** for this task (even if other core threads are idle).
2. Else → try `workQueue.offer(task)`.
3. If the queue is full and threads < `maximumPoolSize` → create a non-core worker.
4. Else → **reject** via the handler.

```
submit ─► threads < core? ──yes──► new core thread
              │no
              ▼
        queue.offer() ok? ──yes──► queued
              │no (full)
              ▼
        threads < max? ──yes──► new non-core thread
              │no
              ▼
          RejectedExecutionHandler
```

**Consequences worth saying out loud:**
- With an **unbounded queue, `maximumPoolSize` is never used** — step 3 never happens. (This is why `newFixedThreadPool` sets core = max.)
- Threads are created **lazily**, on submission. `prestartAllCoreThreads()` warms them up front.
- Rejection policies: `AbortPolicy` (default, throws `RejectedExecutionException`), `CallerRunsPolicy` (submitting thread runs it — natural back-pressure), `DiscardPolicy`, `DiscardOldestPolicy`.
- Internally each thread is wrapped in a `Worker` (extends AQS, implements `Runnable`); the pool's state and worker count are packed into one `AtomicInteger ctl`.

---

## Q-0022 — Do threads in a pool "actually die"?

**Short answer:** Not after each task — that's the whole point of a pool. They die only in specific cases.

Each worker runs a loop roughly like:
```java
while (task != null || (task = getTask()) != null) {
    beforeExecute(...); task.run(); afterExecute(...);
    task = null;
}
processWorkerExit(...);   // thread is leaving -> run() returns -> thread terminates
```
`getTask()` blocks on the queue:
- **Core thread**: `workQueue.take()` — blocks forever, thread stays alive (state `WAITING`).
- **Non-core thread** (or core with `allowCoreThreadTimeOut(true)`): `workQueue.poll(keepAliveTime)` — if nothing arrives in time, returns `null` → loop ends → thread **dies**.

**When a pool thread really dies:**
1. Non-core thread idle longer than `keepAliveTime`.
2. Core thread idle with `allowCoreThreadTimeOut(true)`.
3. `shutdown()` / `shutdownNow()`.
4. **The task threw an uncaught exception via `execute()`** — the worker dies and the pool replaces it with a new one (`processWorkerExit` adds a worker). Via `submit()`, the exception is caught into the `Future`, so the thread survives.

**At the OS level:** a platform Java thread maps 1:1 to an OS thread. When `run()` returns, the Java thread is `TERMINATED`, the OS thread is released and its stack memory freed. A terminated `Thread` object can never be restarted — `start()` again throws `IllegalThreadStateException`. Virtual threads (Java 21) are cheap JVM-managed objects mounted on carrier threads; you don't pool them.

**Follow-up trap:** *"Why doesn't my `main` method exit?"* — a pool you never shut down holds non-daemon threads alive, and the JVM only exits when all non-daemon threads finish.

---

## Q-0023 — Thread lifecycle and management

**`Thread.State` values:**

| State | Enters when | Leaves when |
|---|---|---|
| `NEW` | `new Thread(...)` | `start()` |
| `RUNNABLE` | `start()`; running or ready-to-run (Java doesn't separate them) | blocks / waits / finishes |
| `BLOCKED` | waiting to **acquire a monitor** (`synchronized`) | lock acquired |
| `WAITING` | `wait()`, `join()`, `LockSupport.park()` (incl. `ReentrantLock` waits) — no timeout | `notify`, `unpark`, joined thread ends |
| `TIMED_WAITING` | `sleep(t)`, `wait(t)`, `join(t)`, `parkNanos` | timeout or signal |
| `TERMINATED` | `run()` returned or threw | — |

Subtle point: a thread waiting on a `ReentrantLock` is `WAITING` (parked), not `BLOCKED` — `BLOCKED` is only for intrinsic monitors.

**Pool lifecycle (`ThreadPoolExecutor`):** `RUNNING → SHUTDOWN` (on `shutdown()`) or `→ STOP` (on `shutdownNow()`) `→ TIDYING → TERMINATED`.

**Management toolkit:** `interrupt()` (cooperative cancellation — the task must check `isInterrupted()` or handle `InterruptedException`; never swallow it), `join()`, daemon vs user threads, thread names + `jstack` / `jcmd <pid> Thread.print` for diagnosing deadlocks, `sleep()` keeps locks while `wait()` releases the monitor.

---

## Q-0015 — Types of locks and when to use each

| Mechanism | What it gives | Use when | Caveats |
|---|---|---|---|
| `synchronized` (intrinsic monitor) | Mutual exclusion + visibility, reentrant | Simple critical sections | No timeout, not interruptible, one condition (`wait/notify`) |
| `ReentrantLock` | `tryLock()`, `tryLock(timeout)`, `lockInterruptibly()`, fairness option, multiple `Condition`s | Need to back off / avoid deadlock / multiple wait conditions | Must `unlock()` in `finally` |
| `ReentrantReadWriteLock` | Many readers OR one writer | Read-heavy shared data (config cache) | Write starvation possible; no upgrade read→write |
| `StampedLock` (8) | Optimistic reads (`tryOptimisticRead` + `validate`) | Very read-heavy, short reads | **Not reentrant**, no `Condition`s, easy to misuse |
| `Semaphore` | N permits | Limit concurrency (e.g. max 10 calls to a downstream) | Not ownership-based |
| `volatile` | Visibility + ordering only | Flags (`running = false`), safe publication | No atomicity |
| Atomics / CAS (`AtomicInteger`, `LongAdder`, `ConcurrentHashMap.compute`) | Lock-free atomic updates | Counters, single-variable state | Spinning under heavy contention; `LongAdder` for hot counters |
| **DB optimistic lock** (`@Version`) | Detect concurrent updates at commit | Low-conflict updates across app instances | Retry on `OptimisticLockException` |
| **DB pessimistic lock** (`SELECT … FOR UPDATE`, `@Lock(PESSIMISTIC_WRITE)`) | Row lock held for the transaction | High-conflict, must-not-fail updates (balances) | Deadlock / throughput risk |
| **Distributed lock** (Redis/ZooKeeper/DB) | Mutual exclusion across services | Scheduled job must run on one instance | Lease expiry, fencing tokens |

**The point that separates SDE-2 answers:** a JVM lock only protects **one JVM**. With multiple service instances behind a load balancer (normal for Spring Boot microservices), `synchronized` on a balance update protects nothing — you need the database (or a distributed lock).

Also know: lock coarsening, lock elision and escape analysis exist in the JIT; biased locking was deprecated in JDK 15 and later removed — don't present it as current.

---

## Q-0016 — Scenario: where do you place the lock?

The actual scenarios weren't reported, so practise the **method** plus three standard scenarios.

**Method to talk through (out loud, in this order):**
1. **Identify the shared mutable state** and the **invariant** (e.g. "total money is conserved").
2. **Can I avoid locking?** Immutability, thread confinement, a concurrent collection, or an atomic op.
3. **Lock the invariant, not the field** — every read and write of the state that participates in the invariant uses the *same* lock.
4. **Keep the critical section minimal** — no network/DB/IO calls while holding a lock.
5. **Multiple locks → fixed global ordering** to prevent deadlock; or `tryLock` with timeout.
6. **Multiple JVMs?** → move the lock to the DB / distributed lock.

**Scenario A — money transfer (deadlock trap):**
```java
// BAD: thread1 transfer(a,b), thread2 transfer(b,a) -> each holds one lock, waits for the other.
void transfer(Account from, Account to, long amount) {
    synchronized (from) { synchronized (to) { ... } }
}

// GOOD: always lock in a global order (by id).
void transfer(Account from, Account to, long amount) {
    Account first  = from.id() < to.id() ? from : to;
    Account second = from.id() < to.id() ? to : from;
    synchronized (first) {
        synchronized (second) {
            if (from.balance() < amount) throw new InsufficientFundsException();
            from.debit(amount);
            to.credit(amount);
        }
    }
}
```
Follow-up: "the app runs on 4 pods" → use a DB transaction with `SELECT ... FOR UPDATE` on both rows, locked in id order, or optimistic `@Version` + retry.

**Scenario B — check-then-act on a map (race even with a "thread-safe" map):**
```java
// BAD: two threads both see null and both create.
if (!cache.containsKey(key)) cache.put(key, load(key));
// GOOD: atomic per key.
cache.computeIfAbsent(key, this::load);   // keep load() short; it runs while the bin is locked
```

**Scenario C — lazy singleton (double-checked locking):**
```java
private static volatile Config instance;          // volatile prevents seeing a half-constructed object
static Config get() {
    Config c = instance;
    if (c == null) {
        synchronized (Config.class) {
            c = instance;
            if (c == null) instance = c = new Config();
        }
    }
    return c;
}
// Simpler and preferred: holder idiom or enum singleton.
```

**Scenario D — read-heavy cache refreshed periodically:** `ReentrantReadWriteLock`, or better, build a new immutable map and swap a `volatile` reference (no read locks at all).

**Related practice:** bounded blocking queue with `ReentrantLock` + two `Condition`s (notFull/notEmpty); print odd/even with two threads; thread-safe rate limiter; LeetCode 1114/1115/1116 (concurrency section).
