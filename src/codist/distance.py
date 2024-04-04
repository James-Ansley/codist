from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from . import tree
from .tree import Tree

__all__ = (
    "Cost",
    "tree_dist",
    "tree_edit",
    "Lambda",
    "Change",
)

Lambda: Final[str] = "Λ"
type Change[T] = tuple[T | Lambda, T | Lambda]


@dataclass(frozen=True)
class Cost[T]:
    """
    A set of tree edit cost functions for deleting, inserting
    and relabelling nodes.

    By default, returns 1 except for the case γ(a -> a) which returns 0
    """

    delete: Callable[[T], float] = (lambda n: 1)
    insert: Callable[[T], float] = (lambda n: 1)
    relabel: Callable[[T, T], float] = (lambda n1, n2: 0 if n1 == n2 else 1)


def tree_dist[T](
      tree1: Tree[T],
      tree2: Tree[T],
      cost: Cost = Cost(),
) -> float:
    """
    Tree edit cost using the given cost function.
    """
    postorder1 = tree.postorder(tree1)
    postorder2 = tree.postorder(tree2)
    keyroots1 = tree.keyroots(tree1)
    keyroots2 = tree.keyroots(tree2)
    l1 = tree.leftmosts(tree1)
    l2 = tree.leftmosts(tree2)

    memo = [[0 for _ in postorder2] for _ in postorder1]

    def _tree_dist(i, j):
        forest_dist = [
            [0 for _ in range(j - l2[j] + 2)]
            for _ in range(i - l1[i] + 2)
        ]

        for (i1, ni) in enumerate(range(l1[i], i + 1), start=1):
            forest_dist[i1][0] = \
                forest_dist[i1 - 1][0] + cost.delete(postorder1[ni])

        for (j1, nj) in enumerate(range(l2[j], j + 1), start=1):
            forest_dist[0][j1] = \
                forest_dist[0][j1 - 1] + cost.insert(postorder2[nj])

        for (i1, ni) in enumerate(range(l1[i], i + 1), start=1):
            for (j1, nj) in enumerate(range(l2[j], j + 1), start=1):
                if l1[ni] == l1[i] and l2[nj] == l2[j]:
                    forest_dist[i1][j1] = min(
                        forest_dist[i1 - 1][j1] + cost.delete(postorder1[ni]),
                        forest_dist[i1][j1 - 1] + cost.insert(postorder2[nj]),
                        forest_dist[i1 - 1][j1 - 1]
                        + cost.relabel(postorder1[ni], postorder2[nj]),
                    )
                    memo[ni][nj] = forest_dist[i1][j1]
                else:
                    forest_dist[i1][j1] = min(
                        forest_dist[i1 - 1][j1] + cost.delete(postorder1[ni]),
                        forest_dist[i1][j1 - 1] + cost.insert(postorder2[nj]),
                        forest_dist[l1[ni] - l1[i]][l2[nj] - l2[j]]
                        + memo[ni][nj]
                    )

    for ki in keyroots1:
        for kj in keyroots2:
            _tree_dist(ki, kj)

    return memo[-1][-1]


def tree_edit[T](
      tree1: Tree[T],
      tree2: Tree[T],
      cost: Cost[T] = Cost(),
) -> tuple[float, tuple[Change[T], ...]]:
    """
    Tree edit cost and edit path using the given cost function.
    """
    postorder1 = tree.postorder(tree1)
    postorder2 = tree.postorder(tree2)
    keyroots1 = tree.keyroots(tree1)
    keyroots2 = tree.keyroots(tree2)
    l1 = tree.leftmosts(tree1)
    l2 = tree.leftmosts(tree2)

    memo = [[0 for _ in postorder2] for _ in postorder1]
    ops = [[[] for _ in postorder2] for _ in postorder1]

    def _tree_dist(i, j):
        forest_dist = [
            [0 for _ in range(j - l2[j] + 2)]
            for _ in range(i - l1[i] + 2)
        ]
        opt_parts = [[[] for _ in range(j - l2[j] + 2)]
                     for _ in range(i - l1[i] + 2)]

        for (i1, ni) in enumerate(range(l1[i], i + 1), start=1):
            node = postorder1[ni]
            forest_dist[i1][0] = \
                forest_dist[i1 - 1][0] + cost.delete(node)
            opt_parts[i1][0] = [*opt_parts[i1 - 1][0], (node, Lambda)]

        for (j1, nj) in enumerate(range(l2[j], j + 1), start=1):
            node = postorder2[nj]
            forest_dist[0][j1] = \
                forest_dist[0][j1 - 1] + cost.insert(node)
            opt_parts[0][j1] = [*opt_parts[0][j1 - 1], (Lambda, node)]

        for (i1, ni) in enumerate(range(l1[i], i + 1), start=1):
            for (j1, nj) in enumerate(range(l2[j], j + 1), start=1):
                left = postorder1[ni]
                right = postorder2[nj]
                if l1[ni] == l1[i] and l2[nj] == l2[j]:
                    costs = [
                        forest_dist[i1 - 1][j1] + cost.delete(left),
                        forest_dist[i1][j1 - 1] + cost.insert(right),
                        forest_dist[i1 - 1][j1 - 1]
                        + cost.relabel(left, right),
                    ]
                    forest_dist[i1][j1] = min(costs)
                    memo[ni][nj] = forest_dist[i1][j1]
                    min_cost = min((0, 1, 2), key=lambda i_: costs[i_])
                    if min_cost == 0:
                        opt_parts[i1][j1] = \
                            [*opt_parts[i1 - 1][j1], (left, Lambda)]
                    elif min_cost == 1:
                        opt_parts[i1][j1] = \
                            [*opt_parts[i1][j1 - 1], (Lambda, right)]
                    else:
                        opt_parts[i1][j1] = \
                            [*opt_parts[i1 - 1][j1 - 1], (left, right)]
                    ops[ni][nj] = opt_parts[i1][j1]
                else:
                    m = l1[ni] - l1[i]
                    n = l2[nj] - l2[j]
                    costs = [
                        forest_dist[i1 - 1][j1] + cost.delete(left),
                        forest_dist[i1][j1 - 1] + cost.insert(right),
                        forest_dist[m][n] + memo[ni][nj],
                    ]
                    forest_dist[i1][j1] = min(costs)
                    min_cost = min((0, 1, 2), key=lambda i_: costs[i_])
                    if min_cost == 0:
                        opt_parts[i1][j1] = \
                            [*opt_parts[i1 - 1][j1], (left, Lambda)]
                    elif min_cost == 1:
                        opt_parts[i1][j1] = \
                            [*opt_parts[i1][j1 - 1], (Lambda, right)]
                    else:
                        opt_parts[i1][j1] = \
                            [*opt_parts[m][n], *ops[ni][nj]]

    for ki in keyroots1:
        for kj in keyroots2:
            _tree_dist(ki, kj)

    return memo[-1][-1], tuple(ops[-1][-1])