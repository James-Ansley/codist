from collections.abc import Callable, Hashable
from dataclasses import dataclass
from functools import cache

__all__ = ("Tree", "Forest", "tree", "tree_dist", "forest_dist", "Cost")

type Tree[T: Hashable] = tuple[T, tuple[Tree[T], ...]]
type Forest[T: Hashable] = tuple[Tree[T], ...]


def tree[T](
      value: T,
      children: tuple[Tree[T], ...] | tuple[()] = (),
) -> Tree[T]:
    """Small convenience function to help construct trees"""
    return value, children


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
      tree1: Tree[T] | tuple[()],
      tree2: Tree[T] | tuple[()],
      cost: Cost[T] = Cost(),
) -> float:
    """
    Returns the minimum edit cost to transform tree1 into tree2 with the given
    cost functions.

    Allows for the special cases of the empty trees, ``()``, for tree1
    or tree2.

    A ``Tree[T]`` is a tuple of the form: ``(T, Tree[T]*)``
    i.e. a root node, followed by 0 or more tuples of the same
    ``Tree[T]`` format
    """
    return forest_dist(
        (tree1,) if tree1 else (),
        (tree2,) if tree2 else (),
        cost,
    )


@cache
def forest_dist[T](
      forest1: Forest[T],
      forest2: Forest[T],
      cost: Cost[T] = Cost(),
) -> float:
    """
    Returns the minimum edit cost to transform forest1 into forest2 with the
    given cost functions.

    Given that, a ``Tree[T]`` is a tuple of the form: ``(T, Tree[T]*)``,
    A ``Forest[T]`` is a tuple of the form: ``(Tree[T]*)``
    i.e. 0 or more trees
    """
    if forest1 == () and forest2 == ():
        return 0
    elif forest2 == ():
        left, right = split_rightmost_root(forest1)
        return forest_dist(left, forest2, cost) + cost.delete(right)
    elif forest1 == ():
        left, right = split_rightmost_root(forest2)
        return forest_dist(forest1, left, cost) + cost.insert(right)
    else:
        left, right = split_rightmost_root(forest1)
        cost_1 = forest_dist(left, forest2, cost) + cost.delete(right)

        left, right = split_rightmost_root(forest2)
        cost_2 = forest_dist(forest1, left, cost) + cost.insert(right)

        left_1, right_1 = split_rightmost_root((forest1[-1],))
        left_2, right_2 = split_rightmost_root((forest2[-1],))
        cost_3 = (
              forest_dist(forest1[:-1], forest2[:-1], cost)
              + forest_dist(left_1, left_2, cost)
              + cost.relabel(right_1, right_2)
        )
        return min(cost_1, cost_2, cost_3)


@cache
def split_rightmost_root[T](forest: Forest[T]):
    left, (root, children) = forest[:-1], forest[-1]
    return (*left, *children), root
