"""Test suite for PersistentSegmentTree.py (standard library only).

The interesting tests are the randomised ones: they build a random tree, ask
random questions, and compare against a brute-force BFS that collects and
sorts every value on the path.  That is the only way to trust the four-root
path-combination trick, because the failure modes it hides are all off-by-one
shaped.

Run with:  python -m unittest test_solution -v
"""

import random
import subprocess
import sys
import unittest
from pathlib import Path

import PersistentSegmentTree as pst

SOLUTION = str(Path(__file__).with_name("PersistentSegmentTree.py"))


# ── reference implementation ────────────────────────────────────────────────
def brute_force_path_values(n, vals, edges, u, v):
    """BFS from u to recover the unique u->v path, then collect its values."""
    adj = {i: [] for i in range(1, n + 1)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    prev = {u: None}
    queue = [u]
    while queue:
        cur = queue.pop(0)
        if cur == v:
            break
        for nxt in adj[cur]:
            if nxt not in prev:
                prev[nxt] = cur
                queue.append(nxt)

    path, cur = [], v
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return sorted(vals[node - 1] for node in path)


def build_case(n, vals, edges, queries):
    parts = [f"{n} {len(queries)}", " ".join(map(str, vals))]
    parts += [f"{u} {v}" for u, v in edges]
    parts += [f"{u} {v} {k}" for u, v, k in queries]
    return "\n".join(parts) + "\n"


def run_solver(stdin):
    result = subprocess.run(
        [sys.executable, SOLUTION], input=stdin, capture_output=True, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def random_tree(rng, n):
    order = list(range(1, n + 1))
    rng.shuffle(order)
    edges = []
    for i in range(1, n):
        edges.append((order[i], rng.choice(order[:i])))
    return edges


# ── tests ──────────────────────────────────────────────────────────────────
class TestAgainstBruteForce(unittest.TestCase):
    def assert_matches_brute_force(self, n, vals, edges, queries):
        code, out, _ = run_solver(build_case(n, vals, edges, queries))
        self.assertEqual(code, 0, "solver exited non-zero on a valid case")
        got = out.split("\n") if out else []
        expected = []
        for u, v, k in queries:
            values = brute_force_path_values(n, vals, edges, u, v)
            expected.append(str(values[k - 1]) if 1 <= k <= len(values) else "invalid")
        self.assertEqual(got, expected, f"n={n} vals={vals} edges={edges} q={queries}")

    def test_single_node(self):
        self.assert_matches_brute_force(1, [5], [], [(1, 1, 1)])

    def test_single_node_k_too_large_is_invalid(self):
        self.assert_matches_brute_force(1, [5], [], [(1, 1, 2)])

    def test_two_nodes(self):
        self.assert_matches_brute_force(2, [3, 1], [(1, 2)],
                                        [(1, 2, 1), (2, 1, 2), (1, 1, 1), (1, 1, 2)])

    def test_branching_tree(self):
        self.assert_matches_brute_force(
            5, [5, 3, 8, 1, 9], [(1, 2), (1, 3), (3, 4), (3, 5)],
            [(1, 5, 3), (4, 2, 4), (5, 5, 1), (2, 4, 5)],
        )

    def test_all_values_identical(self):
        self.assert_matches_brute_force(
            6, [7] * 6, [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
            [(1, 6, 4), (6, 1, 6), (3, 3, 1), (2, 5, 3)],
        )

    def test_negative_and_unsorted_values(self):
        self.assert_matches_brute_force(
            4, [-3, 12, -7, 0], [(1, 2), (2, 3), (3, 4)],
            [(1, 4, 4), (4, 1, 1), (1, 4, 5), (2, 3, 2)],
        )

    def test_star_topology(self):
        edges = [(1, i) for i in range(2, 7)]
        self.assert_matches_brute_force(
            6, [9, 1, 4, 4, 7, 2], edges,
            [(2, 3, 1), (6, 5, 2), (2, 6, 5), (1, 1, 1)],
        )

    def test_random_against_brute_force(self):
        rng = random.Random(20240614)
        for _ in range(60):
            n = rng.randint(1, 14)
            vals = [rng.randint(-8, 8) for _ in range(n)]
            edges = random_tree(rng, n)
            queries = [
                (rng.randint(1, n), rng.randint(1, n), rng.randint(1, n + 1))
                for _ in range(rng.randint(1, 6))
            ]
            self.assert_matches_brute_force(n, vals, edges, queries)


class TestMalformedInput(unittest.TestCase):
    def assert_rejected(self, stdin, fragment):
        code, out, err = run_solver(stdin)
        self.assertEqual(code, 2, f"expected exit 2, stdout={out!r} stderr={err!r}")
        self.assertEqual(out, "", "a rejected input must not print answers")
        self.assertIn(fragment, err)

    def test_empty_input(self):
        self.assert_rejected("", "unexpected end of input")

    def test_non_integer_tokens(self):
        self.assert_rejected("hello world", "must be whitespace-separated integers")

    def test_truncated_values(self):
        self.assert_rejected("5 1\n1 2\n1 2\n", "unexpected end of input")

    def test_truncated_query(self):
        self.assert_rejected("1 1\n7\n", "unexpected end of input")

    def test_zero_nodes_rejected(self):
        self.assert_rejected("0 0\n", "n must be at least 1")

    def test_negative_query_count(self):
        self.assert_rejected("1 -1\n7\n", "q must not be negative")

    def test_query_referencing_missing_node(self):
        self.assert_rejected("2 1\n5 7\n1 2\n1 99 1\n", "outside 1..2")

    def test_edge_referencing_missing_node(self):
        self.assert_rejected("2 0\n5 7\n1 42\n", "outside 1..2")

    def test_self_loop_rejected(self):
        self.assert_rejected("2 1\n5 7\n1 1\n1 2 1\n", "self-loop")

    def test_duplicate_edge_breaks_connectivity(self):
        self.assert_rejected("4 1\n1 2 3 4\n1 2\n1 2\n3 4\n1 4 1\n", "cycle")

    def test_cycle_detected_in_solve(self):
        with self.assertRaises(pst.MalformedInput):
            pst.solve(3, [1, 2, 3], [(1, 2), (2, 3), (3, 1)], [(1, 1, 1)])

    def test_error_output_goes_to_stderr(self):
        _, out, err = run_solver("nonsense")
        self.assertEqual(out, "")
        self.assertTrue(err)


class TestZeroQueries(unittest.TestCase):
    def test_zero_queries_produces_no_output(self):
        code, out, err = run_solver("2 0\n4 9\n1 2\n")
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)