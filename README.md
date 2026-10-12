# Persistent Segment Tree — k-th smallest on a tree path

A **persistent (path-copying) segment tree** used to answer *"what is the k-th
smallest value on the path from `u` to `v`?"* in `O(log n)` per query.

Every node gets its own version of the tree. Building a version copies only the
`O(log n)` nodes on the update path, so older versions stay valid and
queryable — no copying of the whole array.

## The problem

You are given a tree where each node holds a value:

```
1        5
       /   \
      2     3
     3     8
    / \   /
   4   5 4
   1   9 1
```

For each query `(u, v, k)`, report the k-th smallest value along the path from
`u` to `v`, counting both endpoints. If the path has fewer than `k` nodes, print
`invalid`.

## The trick

Brute force collects and sorts every value on the path — `O(n log n)` per query.
Instead, store a **root-to-node multiset** for every node:

```
root[u] = root[parent[u]] + { value[u] }
```

The multiset of the full `u -> v` path is then a four-root combination. With
`w = LCA(u, v)`:

```
path(u, v) = root[u] + root[v] - root[w] - root[parent[w]]
```

The `-root[w] - root[parent[w]]` cancels everything above the LCA, which would
otherwise be counted twice.

Descent works the same way as a plain order-statistics segment tree — compare
`k` against the left child's count and go left or right — except all four roots
descend in lockstep, so each level costs four array reads instead of one:

```python
lc = C[L[ru]] + C[L[rv]] - C[L[rl]] - C[L[rr]]
if k <= lc: go left
else:       k -= lc; go right
```

## Complexity

| Operation | Cost |
|---|---|
| Build (all `n` root-to-node versions) | `O(n log n)` |
| Query | `O(log n)` |
| Memory | `O(n log n)` |

Values are coordinate-compressed first, so the segment tree is built over
`m = len(set(values))` distinct positions rather than the raw value range. This
keeps it correct for arbitrarily large or negative values.

## Usage

The program reads a problem instance from stdin and writes one answer per query
to stdout.

```
$ python PersistentSegmentTree.py < input.txt
```

Input format:

```
n q
a1 a2 ... an          value stored at each node
u1 v1                 n-1 edges forming a tree on nodes 1..n
...
u(n-1) v(n-1)
u v k                 q queries
...
```

Example — a chain `1-2-3-4` holding `10 20 30 40`, path `1 -> 4`:

```
$ printf '4 3\n10 20 30 40\n1 2\n2 3\n3 4\n1 4 4\n4 1 1\n1 4 5\n' | python PersistentSegmentTree.py
40
10
invalid
```

- `1 4 4` → path is all four nodes, sorted `[10 20 30 40]`, 4th is `40`
- `4 1 1` → same path, 1st is `10`
- `1 4 5` → the path only has 4 nodes, so `5` is out of range → `invalid`

Malformed input (non-integer tokens, truncated input, a node index outside
`1..n`, a self-loop, or edges that do not form a connected tree) is reported on
**stderr** with exit code `2`, and nothing is written to stdout.

## Requirements

Python 3.8+, standard library only. No external dependencies.

## Tests

```bash
python -m unittest test_solution -v
```

21 tests. The core ones are randomised: each builds a random tree, asks random
questions, and compares against a brute-force BFS that collects and sorts every
value on the path. That cross-check matters because the four-root combination
hides mistakes that only show up as subtle off-by-one errors in the `k`
arithmetic — hand-written cases are not enough to catch them.

The rest cover the input guards and edge cases: single-node trees, a single node
with `k` out of range, all-identical values, negative values, a star topology,
zero queries, and each malformed-input rejection path.

## Files

```
PersistentSegmentTree.py   the solution
test_solution.py           unittest suite, brute-force cross-check included
README.md                  this file
```