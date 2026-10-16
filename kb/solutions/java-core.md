# Solutions — Core Java

Derived content. Status: **Drafted**. Covers Q-0001, Q-0002, Q-0003, Q-0013, Q-0014.

---

## Q-0001 — Java memory management

**Runtime areas:**

| Area | Per | Holds | Error when exhausted |
|---|---|---|---|
| Heap (Young: Eden + 2 Survivors; Old) | JVM | All objects and arrays | `OutOfMemoryError: Java heap space` |
| Stack | Thread | Frames: local primitives, object *references*, return addresses | `StackOverflowError` (deep recursion) |
| Metaspace (Java 8+, native memory; replaced PermGen) | JVM | Class metadata | `OutOfMemoryError: Metaspace` (classloader leaks) |
| Code cache | JVM | JIT-compiled code | JIT disabled / warnings |
| Direct/off-heap memory | JVM | NIO `ByteBuffer.allocateDirect` | `OutOfMemoryError: Direct buffer memory` |

String pool lives on the heap since Java 7.

**Object allocation path:** new objects go to Eden (often via a thread-local allocation buffer — fast, no locking) → survivors after minor GCs → promoted to Old Gen after surviving N cycles. Escape analysis may scalar-replace objects that never leave a method (no heap allocation).

**Can Java leak memory?** Yes — a leak is an object that is still *reachable* but no longer *needed*:
- Static collections that only grow (caches without eviction).
- `ThreadLocal` in pooled threads never `remove()`d (the thread never dies — links to Q-0022).
- Unclosed resources (use try-with-resources).
- Listeners/callbacks never deregistered; inner classes holding outer references.

**How you'd diagnose (say this — it's the practical part):** `-Xlog:gc*` GC logs, `jcmd <pid> GC.heap_info`, heap dump via `-XX:+HeapDumpOnOutOfMemoryError` or `jcmd <pid> GC.heap_dump`, analyse dominator tree in Eclipse MAT / VisualVM.

---

## Q-0002 — String pool

- String literals are stored once in the **string pool** (interned) on the heap; identical literals share one object. This is safe only because `String` is **immutable**.
- `new String("hi")` always creates a new heap object (and the literal `"hi"` in the pool if not already there) — so "how many objects?" → up to 2.
- `intern()` returns the pooled instance.
- Compile-time constant expressions are folded; runtime concatenation creates new objects.

```java
String a = "hello";
String b = "hello";
String c = new String("hello");
String d = "hel" + "lo";            // constant-folded at compile time
String p = "hel";
String e = p + "lo";                // runtime concat (p not final)
final String q = "hel";
String f = q + "lo";                // q is a compile-time constant -> folded

a == b          // true  (same pooled object)
a == c          // false (c is a separate heap object)
a.equals(c)     // true
a == d          // true
a == e          // false
a == f          // true
a == c.intern() // true
```

**Why immutable?** Pool sharing, thread-safety, cached `hashCode` (great as `HashMap` keys), security (class names, file paths, connection URLs can't be mutated after validation).
**Follow-ups:** `StringBuilder` (not synchronized) vs `StringBuffer` (synchronized); why `char[]` is preferred for passwords (can be wiped); Java 9 compact strings (`byte[]` + coder, Latin-1 uses 1 byte/char).

---

## Q-0003 — Java 8 features

1. **Lambdas** — concise implementations of functional interfaces.
2. **Functional interfaces** — single abstract method; `@FunctionalInterface`; built-ins `Function`, `Predicate`, `Consumer`, `Supplier`, `BiFunction`, `UnaryOperator`.
3. **Method references** — `String::length`, `System.out::println`, `ArrayList::new`.
4. **Stream API** — declarative pipelines: `filter`, `map`, `flatMap`, `sorted`, `collect(Collectors.groupingBy(...))`, `reduce`.
5. **Default & static methods in interfaces** — let library authors evolve interfaces (e.g. `Collection.stream()` was added without breaking implementers).
6. **`Optional`** — explicit "may be absent" return type.
7. **`java.time`** — immutable, thread-safe `LocalDate`, `Instant`, `Duration`, `ZonedDateTime` (replacing mutable `Date`/`Calendar` and non-thread-safe `SimpleDateFormat`).
8. **`CompletableFuture`** — composable async.
9. JVM/library: Metaspace replaces PermGen; `ConcurrentHashMap` rewritten (CAS + bin-level locking, no segments); `HashMap` buckets become red-black trees after 8 collisions.

**Follow-ups:**
- *Diamond problem with default methods?* If two interfaces provide the same default, the class must override and can call `A.super.method()`. Class methods always win over interface defaults.
- *`Optional` misuse:* don't use it for fields/parameters, don't call `get()` without checking — use `orElse`, `orElseGet` (lazy), `orElseThrow`, `map`.
- *`map` vs `flatMap`?* `flatMap` flattens `Stream<Stream<T>>` / `Optional<Optional<T>>`.

---

## Q-0013 — Old vs new Java (streams, lambdas, modern Java)

**Before vs after Java 8:**
```java
// Java 7
List<String> names = new ArrayList<>();
for (Employee e : employees) {
    if (e.getSalary() > 50_000) names.add(e.getName().toUpperCase());
}
Collections.sort(names);

// Java 8+
List<String> names = employees.stream()
        .filter(e -> e.getSalary() > 50_000)
        .map(e -> e.getName().toUpperCase())
        .sorted()
        .toList();                          // Java 16+; use collect(Collectors.toList()) on 8
```

**Stream internals that get probed:**
- **Lazy**: intermediate ops do nothing until a terminal op runs.
- **Vertical processing**: each element flows through the whole pipeline; short-circuit ops (`findFirst`, `anyMatch`, `limit`) stop early.
- **Single use**: a consumed stream throws `IllegalStateException`.
- **Stateless vs stateful** ops (`sorted`, `distinct` buffer everything).
- **Parallel streams** use the common `ForkJoinPool`; good for large CPU-bound work on splittable sources (`ArrayList`, arrays), bad for small data, I/O, or `LinkedList`.
- **When a loop is better**: checked exceptions, early `break` with complex state, very hot paths, debugging clarity.
- Lambdas compile to `invokedynamic`, not anonymous inner classes; can only capture *effectively final* locals.

**Post-8 milestones (LTS in bold):**
- 9: modules, `List.of/Map.of`, `Optional.ifPresentOrElse`, JShell.
- 10: `var`. **11**: `String.isBlank/strip/lines/repeat`, standard `HttpClient`.
- 14: switch expressions. 16: **records**, `Stream.toList()`. **17**: sealed classes, pattern matching for `instanceof`.
- **21**: **virtual threads**, pattern matching for `switch`, record patterns, sequenced collections, generational ZGC.

Mastercard round 2 also asked about Spring Boot 3, which **requires Java 17** — so know 17 features cold.

---

## Q-0014 — Garbage collection

**Core idea:** an object is garbage when it is **unreachable from GC roots** (local variables on thread stacks, static fields, active threads, JNI refs). Reference counting is *not* used, so cycles are collected fine.

**Generational hypothesis:** most objects die young → collect Young Gen often (cheap **minor GC**, copying live objects between survivors), Old Gen rarely (**major/mixed/full GC**).

**Phases:** mark (find live objects) → sweep (reclaim) → compact (defragment). "Stop-the-world" pauses suspend application threads.

| Collector | Notes | When |
|---|---|---|
| Serial | Single-threaded | Tiny heaps, containers with 1 CPU |
| Parallel | Throughput-focused, multi-threaded STW | Batch jobs |
| **G1** | **Default since Java 9**; region-based, pause target (`-XX:MaxGCPauseMillis`, default 200ms) | General server apps |
| ZGC | Concurrent, sub-millisecond pauses, huge heaps; generational in 21 | Latency-sensitive services (payments!) |
| Shenandoah | Concurrent compaction | Low latency |

**Reference types:** strong; `SoftReference` (cleared under memory pressure — caches); `WeakReference` (cleared at next GC — `WeakHashMap`); `PhantomReference` (post-mortem cleanup, `Cleaner`).

**Follow-ups:**
- `System.gc()` is only a hint. `finalize()` is deprecated — use try-with-resources / `Cleaner`.
- Frequent full GCs → heap too small, leak, or too many objects promoted early. Tune `-Xms`/`-Xmx` (set equal in containers), check allocation rate, then consider collector.
- "Memory handling" in a project context: reduce allocation (reuse buffers, avoid boxing in hot loops, stream large result sets with pagination instead of loading 1M JPA entities).
