# Solutions — Spring, Spring Boot, Security, JPA

Derived content. Status: **Drafted**. Covers Q-0008 – Q-0012.

---

## Q-0008 — Spring Boot annotations

**Bootstrap & config**
- `@SpringBootApplication` = `@SpringBootConfiguration` (a `@Configuration`) + `@EnableAutoConfiguration` + `@ComponentScan` (from the class's package downward — a common "bean not found" cause).
- `@Configuration` + `@Bean` — explicit bean definitions. Full `@Configuration` classes are CGLIB-proxied so calling one `@Bean` method from another returns the same singleton (`proxyBeanMethods = false` turns that off for faster startup).
- `@Component` vs `@Bean`: `@Component` on your own class (scanned); `@Bean` for third-party classes or conditional/complex construction.
- Stereotypes: `@Service` (semantic), `@Repository` (adds **exception translation** to `DataAccessException`), `@Controller`, `@RestController` (= `@Controller` + `@ResponseBody`).
- `@Value("${x}")` vs `@ConfigurationProperties(prefix = "app")` (type-safe, validated, grouped — preferred).
- `@Profile`, `@Conditional`, `@ConditionalOnProperty`, `@ConditionalOnMissingBean` (how auto-config backs off when you define your own bean).
- `@Primary`, `@Qualifier` — resolving multiple candidates. `@Lazy`, `@Scope("prototype")`.

**Web:** `@RequestMapping`/`@GetMapping`…, `@PathVariable`, `@RequestParam`, `@RequestBody`, `@ResponseStatus`, `@Valid`/`@Validated`, `@RestControllerAdvice` + `@ExceptionHandler` for global error handling.

**Data/tx:** `@Transactional`, `@Entity`, `@Id`, `@GeneratedValue`, `@Version`, `@Query`, `@EnableJpaRepositories`.

**Others:** `@Async` + `@EnableAsync`, `@Scheduled` + `@EnableScheduling`, `@Cacheable` + `@EnableCaching`.

**Proxy gotcha (high-probability follow-up):** `@Transactional`, `@Async`, `@Cacheable` work through proxies, so a call from one method to another **in the same class** (self-invocation) bypasses the proxy and the annotation silently does nothing. Also only `public` methods are proxied by default.

---

## Q-0009 — Spring vs Spring Boot (and Spring Boot 3)

**Ambiguity:** "Spring vs Spring Boot 3" could mean (a) Spring Framework vs Spring Boot, or (b) Spring Boot 2 vs 3. Answer (a) in two sentences, then pivot to (b) — covering both is safe.

**(a) Framework vs Boot**

| Spring Framework | Spring Boot |
|---|---|
| IoC/DI container + modules (MVC, Data, AOP, Tx) | Opinionated layer on top of Spring |
| You configure everything (XML/Java config), deploy WAR to external server | **Auto-configuration** based on classpath + properties |
| Manual dependency version alignment | **Starters** with curated, compatible versions |
| — | **Embedded server** (Tomcat/Jetty/Undertow), runnable fat JAR |
| — | **Actuator** (health, metrics, info), externalized config, profiles |

How auto-config works: `@EnableAutoConfiguration` loads candidates listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Boot 3; was `spring.factories` in Boot 2), each guarded by `@Conditional…` annotations. Debug with `--debug` (condition evaluation report).

**(b) What changed in Spring Boot 3 (Nov 2022)**
- **Java 17 baseline**, built on **Spring Framework 6**.
- **`javax.*` → `jakarta.*`** (Jakarta EE 9+): `jakarta.persistence`, `jakarta.servlet`, `jakarta.validation` — the biggest migration pain.
- **GraalVM native image** support via AOT processing (fast startup, low memory).
- **Observability**: Micrometer Observation API + **Micrometer Tracing** (replaces Spring Cloud Sleuth).
- **RFC 7807 Problem Details** for error responses (`ProblemDetail`).
- **HTTP interface clients** (`@HttpExchange`) — declarative REST clients; Boot 3.2 adds `RestClient`.
- **Spring Security 6**: `WebSecurityConfigurerAdapter` removed → `SecurityFilterChain` bean; `authorizeHttpRequests` + `requestMatchers`.
- Boot 3.2+: `spring.threads.virtual.enabled=true` runs request handling on **virtual threads** (Java 21) — a nice bridge to the concurrency questions.

---

## Q-0010 — Spring Security

**Architecture (draw it):**
```
Request → DelegatingFilterProxy → FilterChainProxy → SecurityFilterChain
          [CorsFilter → CsrfFilter → (Bearer/UsernamePassword)AuthenticationFilter
           → ExceptionTranslationFilter → AuthorizationFilter] → DispatcherServlet → Controller
```
**Authentication flow:** filter extracts credentials → `AuthenticationManager` (`ProviderManager`) → `AuthenticationProvider` (e.g. `DaoAuthenticationProvider` → `UserDetailsService` + `PasswordEncoder`/BCrypt) → authenticated `Authentication` stored in `SecurityContextHolder` (a **ThreadLocal** — doesn't follow you into `@Async` threads unless propagated).

**Stateless JWT REST API (Boot 3 style):**
```java
@Configuration
@EnableMethodSecurity
class SecurityConfig {
    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())                          // OK: stateless, token in header, no cookies
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health", "/auth/**").permitAll()
                .requestMatchers(HttpMethod.POST, "/payments/**").hasRole("MERCHANT")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
            .build();
    }
    @Bean PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(); }
}
```
**Follow-ups:** authentication vs authorization; `hasRole("X")` checks authority `ROLE_X`; method security `@PreAuthorize("hasRole('ADMIN') or #id == authentication.name")`; **when is disabling CSRF wrong?** — when auth uses cookies/sessions (browser sends cookies automatically). JWT trade-offs: stateless and scalable but hard to revoke → short expiry + refresh tokens. CORS for the Angular front end (this was a full-stack role).

---

## Q-0011 — JPA / Hibernate

**Layers:** JPA = specification (`jakarta.persistence`); Hibernate = implementation; Spring Data JPA = repository abstraction on top.

**Entity states:** transient → **managed** (in persistence context) → detached → removed. The **persistence context** is the first-level cache; at flush it performs **dirty checking** — modifying a managed entity inside a transaction is saved without calling `save()`.

**Fetching:** defaults — `@ManyToOne`/`@OneToOne` **EAGER**, `@OneToMany`/`@ManyToMany` **LAZY**. Recommendation: make everything LAZY and fetch explicitly.

**N+1 problem (most likely deep-dive, and it ties to "30% query improvement"):**
```java
List<Order> orders = orderRepo.findAll();       // 1 query
orders.forEach(o -> o.getItems().size());       // +N queries, one per order
```
Fixes: `@Query("select o from Order o join fetch o.items")`, `@EntityGraph(attributePaths = "items")`, `@BatchSize` / `hibernate.default_batch_fetch_size`, or DTO projections. Detect with `spring.jpa.show-sql`, Hibernate statistics, or datasource-proxy.

**`LazyInitializationException`:** accessing a lazy association after the session closes. Fix with fetch joins/DTOs; don't rely on `spring.jpa.open-in-view` (on by default, logs a warning; holds a DB connection for the whole request).

**`@Transactional` essentials:** rolls back on **unchecked** exceptions only by default (`rollbackFor = Exception.class` for checked); propagation `REQUIRED` (default) vs `REQUIRES_NEW` (suspends outer — e.g. audit log that must persist even if payment fails); isolation levels (READ_COMMITTED typical); `readOnly = true` for queries (skips dirty checking); self-invocation pitfall.

**Concurrency:** `@Version` optimistic locking; `@Lock(LockModeType.PESSIMISTIC_WRITE)` → `SELECT … FOR UPDATE`. (Links to Q-0015/Q-0016.)

**Other:** `save` vs `saveAndFlush`; `persist` vs `merge`; batch inserts (`hibernate.jdbc.batch_size`, but `IDENTITY` generation disables JDBC batching — use `SEQUENCE`); second-level cache (Ehcache/Caffeine) for read-mostly reference data; pagination with `Pageable` instead of loading everything.

---

## Q-0012 — Field `@Autowired` vs constructor injection

```java
// Field injection
@Service
class PaymentService {
    @Autowired private FraudClient fraudClient;     // hidden dependency, mutable, null in plain unit tests
}

// Constructor injection (recommended)
@Service
class PaymentService {
    private final FraudClient fraudClient;
    private final LedgerRepository ledger;

    PaymentService(FraudClient fraudClient, LedgerRepository ledger) {   // no @Autowired needed: single constructor (Spring 4.3+)
        this.fraudClient = fraudClient;
        this.ledger = ledger;
    }
}
// With Lombok: @RequiredArgsConstructor on a class with final fields.
```

**Why constructor injection wins:**
1. **Immutability** — fields can be `final`; object is fully initialized after construction.
2. **Explicit, mandatory dependencies** — can't create the object without them; no `NullPointerException` surprises.
3. **Testability** — `new PaymentService(mockFraud, mockLedger)` with no Spring context or reflection.
4. **Design smell detection** — a constructor with 8 parameters signals an SRP violation (ties to SOLID).
5. **Circular dependencies fail fast** at startup (and Spring Boot 2.6+ prohibits circular references by default anyway).

**Setter injection:** for genuinely optional dependencies. **Field injection:** acceptable only in tests (`@Autowired` in `@SpringBootTest`), or legacy code.

**Follow-ups:** how Spring resolves multiple beans of one type (`@Primary`, `@Qualifier`, parameter name); `ObjectProvider<T>` for optional/lazy deps; how to break a genuine circular dependency (redesign, extract a third bean, events, `@Lazy` as a last resort).
