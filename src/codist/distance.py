"""
Functions to compute the edit distance between trees with given cost functions.
"""

from collections.abc import Callable
from typing import Final, TypeVar

from . import tree
from .tree import Lambda, Tree

__all__ = (
    "Cost",
    "tree_dist",
    "tree_edit",
    "Change",
)



T = TypeVar("T")
#: A change operation of the form ``(T | Lambda -> T | Lambda, ctx)``
#: Where ``ctx`` is either an index or Lambda providing some context for
#: the change operation.
#:
#: - For insertions (Λ -> T, ctx), the ctx is the postorder index of the parent
#:   node in tree2 that T is being added under
#: - For deletions (T -> Λ, ctx), the ctx is the postorder index of the node in
#:   tree1 that is deleted
#: - For relabelings (T1 -> T2, ctx), the ctx is the postorder index of the
#:   node in tree1 that is relabeled
#:
#: .. note::
#:     The ctx variable provides some context for change operations, but does
#:     not provide, for example, the indices of the siblings that are inserted
#:     as children of T for an insertion operation.
Change: type[tuple[T | Lambda, T | Lambda, "int | Lambda"]]

type Change[T] = tuple[T | Lambda, T | Lambda, int | Lambda]


class Cost[T]:
    """
    A set of tree edit cost functions for deleting, inserting
    and relabelling nodes.

    By default, returns 1 except for the case γ(a -> a) which returns 0

    :param delete: A cost function, ``(T) -> float``
        for the change operation ``(T -> Λ)``. Default is ``(T) -> 1``
    :param insert: A cost function ``(T) -> float``
        for the change operation ``(Λ -> T)``. Default is ``(T) -> 1``
    :param relabel: A cost function ``(T1, T2) -> float``
        for the change operation ``(T1 -> T2)``.
        Default is ``(T1, T2) -> 0 if T1 == T2 else 1``

    :ivar delete: A cost function, ``(T) -> float``
    :ivar insert: A cost function ``(T) -> float``
    :ivar relabel: A cost function ``(T1, T2) -> float``
    """

    def __init__(
          self,
          delete: Callable[[T], float] = (lambda n: 1),
          insert: Callable[[T], float] = (lambda n: 1),
          relabel: Callable[[T, T], float] = (
                lambda n1, n2: 0 if n1 == n2 else 1
          ),
    ):
        self.delete: Final[Callable[[T], float]] = delete
        self.insert: Final[Callable[[T], float]] = insert
        self.relabel: Final[Callable[[T, T], float]] = relabel


def tree_dist[T](
      tree1: Tree[T],
      tree2: Tree[T],
      cost: Cost = Cost(),
) -> float:
    """
    Tree edit cost using the given cost function.

    :param tree1: the initial tree
    :param tree2: the target tree
    :param cost: a Cost object defining cost functions

    :returns: The edit distance between ``tree1`` and ``tree2``
    """
    keyroots1 = tree.keyroots(tree1)
    keyroots2 = tree.keyroots(tree2)
    postorder1 = tree.postorder(tree1)
    postorder2 = tree.postorder(tree2)
    l1 = tree.leftmosts(tree1)
    l2 = tree.leftmosts(tree2)

    delete = cost.delete
    insert = cost.insert
    relabel = cost.relabel

    memo = [[0 for _ in postorder2] for _ in postorder1]

    def _tree_dist(i, j):
        forest_dist = [
            [0 for _ in range(j - l2[j] + 2)]
            for _ in range(i - l1[i] + 2)
        ]

        for i1, ni in enumerate(range(l1[i], i + 1), start=1):
            forest_dist[i1][0] = forest_dist[i1 - 1][0] + delete(postorder1[ni])

        for j1, nj in enumerate(range(l2[j], j + 1), start=1):
            forest_dist[0][j1] = forest_dist[0][j1 - 1] + insert(postorder2[nj])

        for i1, ni in enumerate(range(l1[i], i + 1), start=1):
            for (j1, nj) in enumerate(range(l2[j], j + 1), start=1):
                node_i = postorder1[ni]
                node_j = postorder2[nj]
                if l1[ni] == l1[i] and l2[nj] == l2[j]:
                    memo[ni][nj] = forest_dist[i1][j1] = min(
                        forest_dist[i1 - 1][j1] + delete(node_i),
                        forest_dist[i1][j1 - 1] + insert(node_j),
                        forest_dist[i1 - 1][j1 - 1] + relabel(node_i, node_j),
                    )
                else:
                    m = l1[ni] - l1[i]
                    n = l2[nj] - l2[j]
                    forest_dist[i1][j1] = min(
                        forest_dist[i1 - 1][j1] + delete(node_i),
                        forest_dist[i1][j1 - 1] + insert(node_j),
                        forest_dist[m][n] + memo[ni][nj]
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

    :param tree1: the initial tree
    :param tree2: the target tree
    :param cost: a Cost object defining cost functions

    :returns: A tuple containing the edit distance between
        ``tree1`` and ``tree2`` and a tuple of `Change` operations where each
        change operation is a 3-tuple of the form
        ``(T | Lambda -> T | Lambda, ctx)``
        where ``Lambda`` is a singleton string: ``"Λ"``
    """
    keyroots1 = tree.keyroots(tree1)
    keyroots2 = tree.keyroots(tree2)
    postorder1 = tree.postorder(tree1)
    postorder2 = tree.postorder(tree2)
    l1 = tree.leftmosts(tree1)
    l2 = tree.leftmosts(tree2)
    p2 = tree.parents(tree2)

    delete = cost.delete
    insert = cost.insert
    relabel = cost.relabel

    memo = [[0 for _ in postorder2] for _ in postorder1]
    ops = [[[] for _ in postorder2] for _ in postorder1]

    def _tree_dist(i, j):
        forest_dist = [
            [0 for _ in range(j - l2[j] + 2)]
            for _ in range(i - l1[i] + 2)
        ]
        opt_parts = [[() for _ in range(j - l2[j] + 2)]
                     for _ in range(i - l1[i] + 2)]

        for i1, ni in enumerate(range(l1[i], i + 1), start=1):
            node = postorder1[ni]
            forest_dist[i1][0] = forest_dist[i1 - 1][0] + delete(node)
            opt_parts[i1][0] = ((i1 - 1, 0), ((node, Lambda, ni),))

        for j1, nj in enumerate(range(l2[j], j + 1), start=1):
            node = postorder2[nj]
            forest_dist[0][j1] = forest_dist[0][j1 - 1] + insert(node)
            opt_parts[0][j1] = ((0, j1 - 1), ((Lambda, node, p2[nj]),))

        for i1, ni in enumerate(range(l1[i], i + 1), start=1):
            for j1, nj in enumerate(range(l2[j], j + 1), start=1):
                left = postorder1[ni]
                right = postorder2[nj]
                if l1[ni] == l1[i] and l2[nj] == l2[j]:
                    min_cost, forest_dist[i1][j1] = min(enumerate((
                        forest_dist[i1 - 1][j1] + delete(left),
                        forest_dist[i1][j1 - 1] + insert(right),
                        forest_dist[i1 - 1][j1 - 1] + relabel(left, right),
                    )), key=lambda e: e[1])
                    memo[ni][nj] = forest_dist[i1][j1]
                    if min_cost == 0:
                        change = (left, Lambda, ni)
                        opt_parts[i1][j1] = ((i1 - 1, j1), (change,))
                    elif min_cost == 1:
                        change = (Lambda, right, p2[nj])
                        opt_parts[i1][j1] = ((i1, j1 - 1), (change,))
                    else:
                        change = (left, right, ni)
                        opt_parts[i1][j1] = ((i1 - 1, j1 - 1), (change,))
                    ops[ni][nj] = _change_path(opt_parts, i1, j1)
                else:
                    m = l1[ni] - l1[i]
                    n = l2[nj] - l2[j]
                    min_cost, forest_dist[i1][j1] = min(enumerate((
                        forest_dist[i1 - 1][j1] + delete(left),
                        forest_dist[i1][j1 - 1] + insert(right),
                        forest_dist[m][n] + memo[ni][nj],
                    )), key=lambda e: e[1])
                    if min_cost == 0:
                        change = (left, Lambda, ni)
                        opt_parts[i1][j1] = ((i1 - 1, j1), (change,))
                    elif min_cost == 1:
                        change = (Lambda, right, p2[nj])
                        opt_parts[i1][j1] = ((i1, j1 - 1), (change,))
                    else:
                        next_op, changes = opt_parts[m][n]
                        opt_parts[i1][j1] = (next_op, changes + ops[ni][nj])

    for ki in keyroots1:
        for kj in keyroots2:
            _tree_dist(ki, kj)

    return memo[-1][-1], tuple(ops[-1][-1])


def _change_path(ops, i, j) -> tuple[Change, ...]:
    next_op, change = ops[i][j]
    result = [*change[::-1]]
    stack = [next_op]
    while stack:
        (i, j) = stack.pop()
        current = ops[i][j]
        if i < 0 or j < 0 or current == ():
            continue
        next_op, change = current
        if change is not None:
            result.extend(change[::-1])
        stack.append(next_op)
    return tuple(reversed(result))
