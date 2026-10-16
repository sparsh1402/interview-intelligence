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

---

## Q-0024 — Find all unique pairs in a sorted array that sum to a target

**Status: Drafted.** Asked at Google (EXP-0002, phone screen, coded in a shared Google Doc). The candidate solved it in Python; this is the Java version.

**1. Problem & assumptions.** Given a **sorted** `int[] arr` and `target`, return every **unique** value pair `[a, b]` with `a + b == target`, `a <= b`, in ascending order of `a`. Each array position is used at most once per pair (so `[4]` with target 8 gives nothing, `[4,4]` gives `[4,4]`).
Example: `[1,2,3,4,5,6,7]`, target 8 → `[[1,7],[2,6],[3,5]]`.

**2. Clarifying questions.**
- Unique by **value** or by **index**? (Duplicates in input → one `[2,6]` or several?)
- Can an element pair with itself (`4 + 4` from a single 4)?
- Negatives? Values near `Integer.MAX_VALUE` (overflow)?
- Return values or indices? Is the array guaranteed sorted, ascending?

**3. Brute force.** Two nested loops over `i < j`, add `[arr[i], arr[j]]` to a `Set` when the sum matches → O(n²) time, O(k) space for k pairs.

**4. Optimized idea — two pointers.** Because the array is sorted, the sum `arr[l] + arr[r]` moves predictably: moving `l` right can only increase it, moving `r` left can only decrease it. So each step safely discards one element: if the sum is too small, `arr[l]` can't pair with anything left of `r` either (all smaller), so discard `l`; symmetric for too large. Each element is discarded once → O(n).

**5. Algorithm.**
1. `l = 0`, `r = n - 1`.
2. While `l < r`: compute `sum` as `long`.
   - `sum == target` → record pair; then advance `l` past every copy of `arr[l]` and move `r` past every copy of `arr[r]` (this is what makes pairs unique).
   - `sum < target` → `l++`. `sum > target` → `r--`.
3. Pairs come out in ascending order of the smaller element automatically.

**6. Java 17.**
```java
import java.util.*;

public final class PairSum {
    public static List<List<Integer>> findPairs(int[] arr, int target) {
        List<List<Integer>> result = new ArrayList<>();
        int left = 0, right = arr.length - 1;
        while (left < right) {
            long sum = (long) arr[left] + arr[right];   // long: no overflow near Integer.MAX_VALUE
            if (sum == target) {
                result.add(List.of(arr[left], arr[right]));
                int lv = arr[left], rv = arr[right];
                while (left < right && arr[left] == lv) left++;    // skip duplicates of the used left value
                while (left < right && arr[right] == rv) right--;  // skip duplicates of the used right value
            } else if (sum < target) {
                left++;
            } else {
                right--;
            }
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(findPairs(new int[]{1, 2, 3, 4, 5, 6, 7}, 8));        // [[1, 7], [2, 6], [3, 5]]
        System.out.println(findPairs(new int[]{1, 1, 2, 2, 3, 4, 6, 6, 7}, 8));  // [[1, 7], [2, 6]]
        System.out.println(findPairs(new int[]{4, 4}, 8));                       // [[4, 4]]
        System.out.println(findPairs(new int[]{-3, -1, 0, 2, 4, 5}, 1));         // [[-3, 4], [-1, 2]]
    }
}
```
**Why it works:** the invariant is "no valid pair uses an element outside `[l, r]` that we haven't already recorded". Every move discards an element that provably can't form a new pair, so nothing is missed; skipping equal values after a match guarantees no duplicate pair. (Verified by compiling and running the cases above.)

**7. Complexity.** Each pointer moves at most n times in total, including the duplicate-skipping loops → **O(n) time**. **O(1) extra space** besides the output.

**8. Dry run** on `[1,1,2,2,3,4,6,6,7]`, target 8:
| l (val) | r (val) | sum | action |
|---|---|---|---|
| 0 (1) | 8 (7) | 8 | record [1,7]; skip 1s → l=2; skip 7 → r=7 |
| 2 (2) | 7 (6) | 8 | record [2,6]; skip 2s → l=4; skip 6s → r=5 |
| 4 (3) | 5 (4) | 7 | < 8 → l=5 |
| stop (l == r) | | | result `[[1,7],[2,6]]` |

**9. Edge cases & tests.** `[]` and `[x]` → `[]`; no match → `[]`; all equal `[4,4,4,4]`, target 8 → `[[4,4]]` once; negatives; target that would overflow `int` when summed.

**10. Alternatives.**
- **HashSet** (works on unsorted input): O(n) time, O(n) space; to dedupe, store pairs as `min,max` in a `Set` or count values in a `HashMap`.
- **Binary search** for `target - arr[i]` per element: O(n log n), worse than two pointers but a fine stepping stone to say out loud.

**11. Follow-ups & answers.**
- *Unsorted array?* HashSet/HashMap O(n), or sort first O(n log n) then two pointers.
- *Count pairs by index, duplicates included?* On a match with equal values (`arr[l] == arr[r]`), add `C(m, 2)` for m copies; otherwise add `countL × countR`.
- *Return indices instead?* Classic Two Sum (LC 1) with a `HashMap<value, index>`.
- *3Sum / 4Sum?* Fix one (or two) elements and run this two-pointer routine on the rest: O(n²) / O(n³).
- *Data too big for memory / streaming?* Hash-partition values by `v` and `target - v` into the same bucket, then solve each bucket.
- *Google Doc, no IDE:* say your test cases out loud and trace one before declaring done; that is what the interviewer grades.

**12. Related practice.** LC 1 (Two Sum), 167 (Two Sum II sorted), 15 (3Sum), 18 (4Sum), 16 (3Sum Closest), 1679 (Max Number of K-Sum Pairs), 532 (K-diff Pairs).

---

## Q-0025 — Lowest common ancestor in a binary tree

**Status: Drafted.** Asked at Google (EXP-0002, on-site round 1, trees & graphs). Follow-up Q-0026.

**1. Problem & assumptions.** Given the root of a binary tree (not a BST) and two node references `p`, `q`, return their lowest common ancestor: the deepest node that has both as descendants, where a node counts as its own descendant. Assume both nodes exist and values may repeat (compare references, not values).

**2. Clarifying questions.**
- Are `p` and `q` guaranteed to be in the tree? (Changes the algorithm — see follow-ups.)
- Can a node be its own ancestor? (Standard: yes.)
- Do nodes have parent pointers? Values unique?
- How deep can the tree be? (Recursion depth / stack overflow in Java for ~10⁵ skewed nodes.)

**3. Brute force.** Find the root-to-`p` path and root-to-`q` path (two DFS traversals storing the path), then walk both paths together; the last common node is the LCA. O(n) time, O(n) space — correct, but two passes and extra lists.

**4. Optimized idea — single post-order DFS.** Ask each subtree "which of p/q did you find?". A subtree returns `p` or `q` if it contains one, the LCA if it contains both, or `null`. The first node where **both** children report something is the split point — the LCA. If the current node is `p` or `q` itself, return it immediately: if the other target is below it, this node is the LCA anyway.

**5. Algorithm.**
1. If `node` is `null`, `p`, or `q` → return `node`.
2. `left = lca(node.left)`, `right = lca(node.right)`.
3. Both non-null → return `node`. Otherwise return whichever is non-null (or `null`).

**6. Java 17.**
```java
public final class LowestCommonAncestor {
    static final class TreeNode {
        int val; TreeNode left, right;
        TreeNode(int val) { this.val = val; }
    }

    public static TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        if (root == null || root == p || root == q) return root;
        TreeNode left = lowestCommonAncestor(root.left, p, q);
        TreeNode right = lowestCommonAncestor(root.right, p, q);
        if (left != null && right != null) return root;   // p and q are on different sides
        return left != null ? left : right;               // both on one side, or none found
    }

    // Follow-up: p or q may be missing from the tree -> return null in that case.
    public static TreeNode lcaIfBothPresent(TreeNode root, TreeNode p, TreeNode q) {
        int[] found = {0};
        TreeNode candidate = dfs(root, p, q, found);
        return found[0] == 2 ? candidate : null;
    }
    private static TreeNode dfs(TreeNode node, TreeNode p, TreeNode q, int[] found) {
        if (node == null) return null;
        TreeNode left = dfs(node.left, p, q, found);    // no early return: explore both sides
        TreeNode right = dfs(node.right, p, q, found);  // so both targets get counted
        if (node == p || node == q) { found[0]++; return node; }
        if (left != null && right != null) return node;
        return left != null ? left : right;
    }
}
```
**Why it works:** by induction on subtree size, the call on any subtree returns non-null exactly when the subtree contains p or q; the LCA is the unique node where p and q first appear in different subtrees (or where one of them is the node itself). The early return in step 1 is safe only because both nodes are guaranteed to exist — which is why the "may be missing" variant drops it and counts instead. (Verified against the tree below.)

**7. Complexity.** Each node visited once → **O(n) time**. Recursion stack **O(h)** — O(log n) balanced, O(n) for a skewed tree.

**8. Dry run.** Tree `3 → (5 → 6, 2 → (7, 4)), (1 → 0, 8)`, p = 7, q = 6:
- At 5: left (6) returns 6. Right (2): its left returns 7, right (4) returns null → 2 returns 7.
- At 5: left = 6, right = 7, both non-null → return 5.
- At 3: left = 5, right (subtree 1) = null → return 5. **LCA = 5** ✔
Other checks: (5, 1) → 3; (5, 4) → 5 (a node is its own ancestor).

**9. Edge cases & tests.** p == q → that node; p is ancestor of q → p; root is p; single-node tree; deep skewed tree (stack depth); p or q absent (use the counting variant).

**10. Alternatives.**
- **Parent map + set:** BFS/DFS to record each node's parent, put all ancestors of p in a `HashSet`, walk up from q until hitting the set. O(n) time and space, but **iterative** — no stack overflow on deep trees.
- **With parent pointers (LC 1650):** like intersecting two linked lists — O(h) time, O(1) space.
- **Many queries on a static tree:** binary lifting (O(log n) per query after O(n log n) preprocessing) or Euler tour + RMQ.

**11. Follow-ups & answers.**
- *BST?* → Q-0026.
- *Nodes might not exist?* → `lcaIfBothPresent` above (LC 1644).
- *Iterative / recursion limits?* Parent-map approach; Java's default thread stack overflows around tens of thousands of frames.
- *LCA of many nodes (LC 1676)?* Put targets in a `Set`, same DFS checking set membership.
- *N-ary tree?* Count non-null child results; if ≥ 2, current node is the LCA.

**12. Related practice.** LC 236, 235, 1644, 1650, 1676, 865 (smallest subtree with all deepest nodes), 1123, 2096 (directions between two nodes — uses LCA).

---

## Q-0026 — Lowest common ancestor in a BST (follow-up to Q-0025)

**Status: Drafted.** Asked at Google as a follow-up. The candidate's answer — "compare values with root to choose the subtree" — is the right idea; here it is precisely.

**1. Problem.** Same as Q-0025, but the tree is a **binary search tree** (left < node < right).

**2. Clarifying questions.** Duplicates allowed, and on which side? Are both nodes guaranteed present? (If not, verify each with a BST search, O(h).)

**3. Brute force.** Reuse Q-0025's O(n) DFS — correct but ignores the ordering.

**4. Optimized idea.** In a BST, values tell you where p and q live. Let `lo = min(p, q)`, `hi = max(p, q)`. If the current node is smaller than `lo`, both are to the right; bigger than `hi`, both are to the left; otherwise the current node **splits** them (or is one of them) — that is the LCA. Only one root-to-node path is walked.

**5. Algorithm.** Start at root; loop: `cur.val < lo` → go right; `cur.val > hi` → go left; else return `cur`.

**6. Java 17 (iterative, O(1) space).**
```java
public static TreeNode lcaBst(TreeNode root, TreeNode p, TreeNode q) {
    int lo = Math.min(p.val, q.val), hi = Math.max(p.val, q.val);
    TreeNode cur = root;
    while (cur != null) {
        if (cur.val < lo) cur = cur.right;        // both targets are larger -> go right
        else if (cur.val > hi) cur = cur.left;    // both targets are smaller -> go left
        else return cur;                          // lo <= cur.val <= hi -> split point
    }
    return null;                                   // only if the nodes aren't in the tree
}
```
**Why it works:** while `cur` is outside `[lo, hi]`, both targets are in the same subtree, so `cur` can't be the LCA and the subtree we move into contains both. The first node inside `[lo, hi]` has p and q on different sides (or is one of them), so it's the deepest common ancestor.

**7. Complexity.** **O(h) time** (log n balanced, n skewed), **O(1) space** iteratively — the point the interviewer is looking for vs. Q-0025's O(n).

**8. Dry run.** BST `6 → (2 → 0, 4 → (3, 5)), (8 → 7, 9)`:
- p=2, q=8: 6 is in [2, 8] → **6**.
- p=3, q=5: 6 > 5 → left to 2; 2 < 3 → right to 4; 4 in [3, 5] → **4**. ✔ (Verified by running.)

**9. Edge cases.** p is ancestor of q (returns p); p == q; nodes not in tree (returns a wrong "split" unless you verify presence); skewed BST (O(n)).

**10–11. Follow-ups.** *Why not use this on a normal binary tree?* Values carry no position information there. *Recursive version?* Same logic, O(h) stack. *Presence not guaranteed?* Two O(h) searches first.

**12. Related practice.** LC 235, 98 (validate BST), 230 (kth smallest), 450 (delete node in BST), 1382 (balance a BST).
