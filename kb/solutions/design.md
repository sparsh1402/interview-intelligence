# Solutions — OOD, SOLID, Design Patterns

Derived content. Status: **Drafted**. Covers Q-0006, Q-0007, Q-0019.

Interview technique: for every principle/pattern give **definition → violation → fix → where I've seen it (Spring/JDK/my project)**. Rapid-fire interviewers reward the "where I've seen it" part most.

---

## Q-0006 — SOLID

**S — Single Responsibility:** a class has one reason to change.
Violation: `PaymentService` validates, charges, sends emails, writes audit logs. Fix: `PaymentValidator`, `PaymentProcessor`, `NotificationService`, `AuditService`.

**O — Open/Closed:** open for extension, closed for modification.
```java
// Violation: every new payment method edits this switch
double fee(String method, double amt) { switch (method) { case "CARD": ...; case "UPI": ...; } }

// Fix: new method = new class, no edits
interface FeePolicy { boolean supports(PaymentMethod m); BigDecimal fee(BigDecimal amount); }
@Component class CardFee implements FeePolicy { ... }
@Component class UpiFee  implements FeePolicy { ... }
@Service class FeeService {
    private final List<FeePolicy> policies;                 // Spring injects all implementations
    FeeService(List<FeePolicy> policies) { this.policies = policies; }
    BigDecimal fee(PaymentMethod m, BigDecimal amt) {
        return policies.stream().filter(p -> p.supports(m)).findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Unsupported " + m)).fee(amt);
    }
}
```

**L — Liskov Substitution:** subtypes must be usable wherever the base type is, without breaking expectations.
Classic violation: `Square extends Rectangle` — `setWidth` also changes height, breaking code that assumes independent sides. Another: a `ReadOnlyList` throwing `UnsupportedOperationException` from `add` (JDK's `List.of` does exactly this — a known trade-off).

**I — Interface Segregation:** clients shouldn't depend on methods they don't use. Split a fat `Worker { work(); eat(); }` into `Workable`, `Feedable`. Spring Data does this well: `CrudRepository`, `PagingAndSortingRepository`, `JpaRepository`.

**D — Dependency Inversion:** high-level modules depend on abstractions, not concretions. `OrderService` depends on `PaymentGateway` interface; `StripeGateway`/`MockGateway` implement it. **DI (Spring) is a mechanism that makes DIP easy — they are not the same thing** (a common confusion worth stating).

---

## Q-0007 — Object-oriented design understanding

The specific questions were not reported. Prepare:
- **Four pillars** with a one-line example each: encapsulation (private state + invariants enforced by methods), abstraction (interface hides implementation), inheritance (is-a reuse), polymorphism (compile-time overloading vs runtime overriding / dynamic dispatch).
- **Composition over inheritance** — inheritance couples you to the parent's implementation (fragile base class); composition + interfaces is more flexible.
- **Coupling and cohesion** — aim for low coupling, high cohesion.
- **Abstract class vs interface (post Java 8)** — abstract class: state, constructors, single inheritance; interface: multiple inheritance of type, default methods but no instance state.
- **`equals`/`hashCode` contract** and why it matters for `HashMap` keys.
- **Immutability** — final class, private final fields, no setters, defensive copies; or `record`.
- Be ready for a **mini LLD** (parking lot, vending machine, payment processor) where they watch you apply all of the above.

---

## Q-0019 — Design patterns with examples

| Pattern | Intent | Where it shows up (say these) |
|---|---|---|
| **Singleton** | One instance | Spring beans are singletons per container (not per JVM, unlike GoF Singleton); enum singleton is the safest hand-written form |
| **Factory / Factory Method** | Hide object creation | `BeanFactory`, `Calendar.getInstance()`, choosing a `PaymentProcessor` by type |
| **Builder** | Construct complex objects step by step | Lombok `@Builder`, `HttpRequest.newBuilder()`, `StringBuilder`, `UriComponentsBuilder` |
| **Prototype** | Clone instances | `@Scope("prototype")` |
| **Adapter** | Convert one interface to another | `HandlerAdapter` in Spring MVC, `Arrays.asList`, wrapping a legacy bank API |
| **Decorator** | Add behaviour without subclassing | `BufferedInputStream(new FileInputStream())`, `Collections.unmodifiableList` |
| **Proxy** | Control access / add cross-cutting logic | **Spring AOP** — `@Transactional`, `@Async`, `@Cacheable` (JDK dynamic proxy or CGLIB) |
| **Facade** | Simplified interface to a subsystem | A service orchestrating fraud check + ledger + notification |
| **Strategy** | Swap algorithms at runtime | Fee/discount policies (SOLID example above), `Comparator` |
| **Observer** | Publish/subscribe | `ApplicationEventPublisher` + `@EventListener`, Kafka consumers |
| **Template Method** | Fixed skeleton, variable steps | `JdbcTemplate`, `RestTemplate`, `AbstractController` |
| **Chain of Responsibility** | Pass request along handlers | **Spring Security filter chain**, servlet filters, validation pipelines |
| **Command** | Encapsulate a request as an object | `Runnable` tasks submitted to an `ExecutorService` |

**Thread-safe Singleton options** (ties the concurrency round to patterns): eager static final; holder idiom; double-checked locking with `volatile` (see concurrency.md Q-0016); `enum`. Enum is reflection- and serialization-safe.

**How to answer "which patterns have you used?"** Pick 2–3 from **your actual Amdocs work** and describe the problem they solved. This requires your input — list the real cases and I'll help shape them.

**Follow-ups:** Strategy vs State; Decorator vs Proxy (decorator adds behaviour the client asks for; proxy controls access transparently); Factory vs Abstract Factory; why Singleton is often called an anti-pattern (global state, hard to test) and why Spring-managed singletons avoid most of that.
