# Solutions — DSA

Derived content. Covers Q-0020.

---

## Q-0020 — "DSA problem – HashMap + sorting (moderate/easy level)"

**Status: Needs-details.** The source does not say which problem was asked. Below is a **practice proxy** — the most common problem shape that matches "HashMap + sorting, easy/medium". It is **not** the reported question. If you find the actual problem, add it as a new appearance and I'll solve it properly.

Practice set that fits the description (any could have been the real one): Sort Array by Increasing Frequency (LC 1636), Sort Characters by Frequency (LC 451), Top K Frequent Elements (LC 347), Top K Frequent Words (LC 692), Group Anagrams (LC 49), Relative Sort Array (LC 1122), Sort employees by department then salary.

### Proxy problem: Sort elements by frequency

**1. Problem & assumptions.** Given `int[] nums`, return the elements sorted by frequency **descending**; ties broken by value **ascending**. Each element appears as many times as in the input.
Example: `[4,6,2,6,4,4,2,6,1]` → `[4,4,4,6,6,6,2,2,1]`.

**2. Clarifying questions to ask.**
- Descending or ascending frequency? Tie-break rule (by value, or by first occurrence)?
- Return all occurrences or just distinct values? Top K only?
- Range of values (negatives? small range → counting array instead of HashMap)?
- Input size (affects whether O(n log n) is fine)?
- Can I modify the input?

**3. Brute force.** For each element, count its frequency by scanning the array (O(n²)), then sort with a comparator that recounts → O(n² log n). Mention it in one line and move on.

**4. Optimized idea.** Count once with a `HashMap` (O(n)). Sort only the **distinct** keys (d ≤ n) by (frequency desc, value asc), then expand each key `freq` times.

**5. Algorithm.**
1. `freq = {}`; for each `x`: `freq[x]++`.
2. `keys = list(freq.keySet())`.
3. Sort `keys` with comparator: higher frequency first; if equal, smaller value first.
4. Write each key `freq[key]` times into the result.

**6. Java 17 implementation.**
```java
import java.util.*;

public final class FrequencySort {

    public static int[] sortByFrequency(int[] nums) {
        Map<Integer, Integer> freq = new HashMap<>();
        for (int x : nums) {
            freq.merge(x, 1, Integer::sum);            // count in one pass
        }

        List<Integer> keys = new ArrayList<>(freq.keySet());
        keys.sort((a, b) -> {
            int fa = freq.get(a), fb = freq.get(b);
            if (fa != fb) return Integer.compare(fb, fa); // frequency descending
            return Integer.compare(a, b);                 // value ascending on ties
        });

        int[] result = new int[nums.length];
        int i = 0;
        for (int key : keys) {
            for (int c = freq.get(key); c > 0; c--) {
                result[i++] = key;
            }
        }
        return result;
    }

    // Variant: top K most frequent values in O(n) using bucket sort.
    public static List<Integer> topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> freq = new HashMap<>();
        for (int x : nums) freq.merge(x, 1, Integer::sum);

        @SuppressWarnings("unchecked")
        List<Integer>[] buckets = new List[nums.length + 1];   // index = frequency
        freq.forEach((value, f) -> {
            if (buckets[f] == null) buckets[f] = new ArrayList<>();
            buckets[f].add(value);
        });

        List<Integer> out = new ArrayList<>(k);
        for (int f = buckets.length - 1; f > 0 && out.size() < k; f--) {
            if (buckets[f] == null) continue;
            for (int v : buckets[f]) {
                if (out.size() == k) break;
                out.add(v);
            }
        }
        return out;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(sortByFrequency(new int[]{4, 6, 2, 6, 4, 4, 2, 6, 1})));
        // [4, 4, 4, 6, 6, 6, 2, 2, 1]
        System.out.println(topKFrequent(new int[]{1, 1, 1, 2, 2, 3}, 2));   // [1, 2]
    }
}
```
**Why it works:** the comparator defines a total order on distinct values consistent with the spec; because we sort keys rather than the n-element array, equal values stay grouped automatically, and expansion restores the original multiplicities.

**7. Complexity.** Counting O(n); sorting d distinct keys O(d log d); expansion O(n). Total **O(n + d log d)** time, worst case O(n log n) when all distinct. Space **O(d)** for the map + O(n) output. Bucket variant: O(n) time, O(n) space.

**8. Dry run** on `[4,6,2,6,4,4,2,6,1]`:
- `freq = {4:3, 6:3, 2:2, 1:1}`
- Sort keys: 4 vs 6 → both 3, 4 < 6 → 4 first; then 2 (freq 2); then 1 (freq 1) → `[4, 6, 2, 1]`
- Expand: `4,4,4, 6,6,6, 2,2, 1` ✔

**9. Edge cases & tests.**
| Input | Expected | Why |
|---|---|---|
| `[]` | `[]` | empty |
| `[7]` | `[7]` | single |
| `[5,5,5]` | `[5,5,5]` | one distinct |
| `[3,1,2]` | `[1,2,3]` | all ties → value order |
| `[-1,-1,2]` | `[-1,-1,2]` | negatives |
| 10⁵ distinct | sorted asc | worst-case sort path |

**10. Alternatives.**
- Sort the boxed array directly with a comparator using `freq` — simpler, O(n log n), more boxing.
- Values in a small known range → `int[] count` instead of `HashMap` (faster, no boxing).
- Top-K only → min-heap of size k: O(n log k); or bucket sort O(n); or quickselect average O(n).
- Tie-break by first occurrence → record first index in a second map (or use `LinkedHashMap` + stable sort).

**11. Likely follow-ups & answers.**
- *Why not `TreeMap`?* Orders by key, not by frequency.
- *Stream version?* `Arrays.stream(nums).boxed().sorted(Comparator.comparing((Integer x) -> freq.get(x)).reversed().thenComparing(Comparator.naturalOrder()))` — fine to show, explain it's the same O(n log n).
- *Comparator pitfall:* never use `fb - fa` subtraction for general ints (overflow) — use `Integer.compare`.
- *How does HashMap work internally?* (very likely at Mastercard given the Java focus): array of buckets, `hash()` spreads high bits, index = `hash & (n-1)`, collisions chained, treeified to red-black tree when a bucket exceeds 8 entries and capacity ≥ 64, resize at load factor 0.75 doubling capacity. Not thread-safe → `ConcurrentHashMap`.
- *Streaming data / doesn't fit in memory?* Count-Min Sketch or partition by hash and merge; Heavy Hitters.

**12. Related practice.** LC 347, 451, 692, 1636, 49, 1122, 387 (first unique char), 242 (valid anagram), 128 (longest consecutive sequence), 560 (subarray sum equals K — HashMap + prefix sums).
