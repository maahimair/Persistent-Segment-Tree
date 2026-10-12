"""Persistent segment tree: k-th smallest value on a tree path.

Competitive-programming style: read the whole problem from stdin, write one
answer per query to stdout.

Input
-----
    n q
    a1 a2 ... an          value stored at each node
    u1 v1                 n-1 edges forming a tree on 1..n
    ...
    u(n-1) v(n-1)
    u v k                 q queries
    ...

Output
------
    one line per query: the k-th smallest value on the path u -> v
    (inclusive of both endpoints), or ``invalid`` when the path holds fewer
    than k nodes.

Approach
--------
Coordinate-compress the values, then build one persistent (path-copying)
segment tree per node.  ``root[u]`` is the root-to-u multiset, which is
``root[parent[u]]`` plus ``a[u]``.  The multiset of the u -> v path is the
standard four-root combination

    path(u, v) = root[u] + root[v] - root[lca] - root[parent(lca)]

and walking those four roots in lockstep descends to the k-th smallest value
in O(log m) without materialising the path.
"""

import sys
from collections import deque

INVALID = "invalid"


class MalformedInput(Exception):
    """Raised when stdin does not describe a valid problem instance."""


def parse(tokens):
    """Validate the token stream and return (n, q, vals, edges, queries)."""
    it = iter(tokens)

    def take(count, what):
        chunk = []
        for _ in range(count):
            try:
                chunk.append(next(it))
            except StopIteration:
                raise MalformedInput(f"unexpected end of input while reading {what}")
        return chunk

    n, q = take(2, "the node and query counts")
    if n < 1:
        raise MalformedInput("n must be at least 1")
    if q < 0:
        raise MalformedInput("q must not be negative")

    vals = take(n, "the node values")
    edges = take(2 * (n - 1), "the tree edges")

    edge_list = []
    for i in range(n - 1):
        u, v = edges[2 * i], edges[2 * i + 1]
        if not (1 <= u <= n) or not (1 <= v <= n):
            raise MalformedInput(f"edge {u}-{v} refers to a node outside 1..{n}")
        if u == v:
            raise MalformedInput(f"edge {u}-{v} is a self-loop, not a tree")
        edge_list.append((u, v))

    queries = []
    for i in range(1, q + 1):
        u, v, k = take(3, f"query {i}")
        if not (1 <= u <= n) or not (1 <= v <= n):
            raise MalformedInput(f"query {i} refers to a node outside 1..{n}")
        queries.append((u, v, k))

    return n, q, vals, edge_list, queries


def solve(n, vals, edges, queries):
    comp = sorted(set(vals))
    m = len(comp)
    idx = {v: i for i, v in enumerate(comp)}

    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)

    # ── persistent segment tree over the compressed value axis ──────────────
    L = [0]
    R = [0]
    C = [0]

    def nn(l=0, r=0, c=0):
        L.append(l)
        R.append(r)
        C.append(c)
        return len(C) - 1

    def upd(p, l, r, x):
        cur = nn(L[p], R[p], C[p] + 1)
        if l + 1 == r:
            return cur
        mid = (l + r) // 2
        if x < mid:
            L[cur] = upd(L[p], l, mid, x)
        else:
            R[cur] = upd(R[p], mid, r, x)
        return cur

    def kth(ru, rv, rl, rr, l, r, k):
        """Descend the four roots in lockstep to the k-th smallest value."""
        while l + 1 < r:
            mid = (l + r) // 2
            lc = C[L[ru]] + C[L[rv]] - C[L[rl]] - C[L[rr]]
            if k <= lc:
                ru, rv, rl, rr = L[ru], L[rv], L[rl], L[rr]
                r = mid
            else:
                k -= lc
                ru, rv, rl, rr = R[ru], R[rv], R[rl], R[rr]
                l = mid
        return l

    # ── root the tree at 1, then build binary lifting for LCA ───────────────
    par = [0] * (n + 1)
    depth = [0] * (n + 1)
    order = []
    seen = [False] * (n + 1)
    dq = deque([1])
    seen[1] = True
    while dq:
        u = dq.popleft()
        order.append(u)
        for v in g[u]:
            if v == par[u]:
                continue
            if seen[v]:
                raise MalformedInput("the supplied edges contain a cycle, not a tree")
            seen[v] = True
            par[v] = u
            depth[v] = depth[u] + 1
            dq.append(v)

    if len(order) != n:
        raise MalformedInput("the supplied edges do not connect all n nodes")

    LOG = n.bit_length()
    up = [par[:] for _ in range(LOG)]
    for k in range(1, LOG):
        for v in range(1, n + 1):
            up[k][v] = up[k - 1][up[k - 1][v]]

    root = [0] * (n + 1)
    for u in order:
        root[u] = upd(root[par[u]] if par[u] else 0, 0, m, idx[vals[u - 1]])

    def lca(u, v):
        if depth[u] < depth[v]:
            u, v = v, u
        diff = depth[u] - depth[v]
        k = 0
        while diff:
            if diff & 1:
                u = up[k][u]
            diff >>= 1
            k += 1
        if u == v:
            return u
        for k in range(LOG - 1, -1, -1):
            if up[k][u] != up[k][v]:
                u = up[k][u]
                v = up[k][v]
        return up[0][u]

    # ── answer ──────────────────────────────────────────────────────────────
    out = []
    for u, v, kq in queries:
        anc = lca(u, v)
        pl = up[0][anc]
        rpar = root[pl] if pl else 0
        tot = C[root[u]] + C[root[v]] - C[root[anc]] - C[rpar]
        if not 1 <= kq <= tot:
            out.append(INVALID)
        else:
            out.append(str(comp[kth(root[u], root[v], root[anc], rpar, 0, m, kq)]))
    return out


def main(argv=None):
    raw = sys.stdin.read().split()
    try:
        tokens = list(map(int, raw))
    except ValueError:
        sys.stderr.write("error: input must be whitespace-separated integers\n")
        return 2
    try:
        n, q, vals, edges, queries = parse(tokens)
        answers = solve(n, vals, edges, queries)
    except MalformedInput as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2

    sys.stdout.write("\n".join(answers))
    if answers:
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())