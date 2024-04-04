from collections.abc import Hashable

__all__ = ("Tree", "Forest", "t", "postorder", "keyroots", "leftmosts")

type Tree[T: Hashable] = tuple[T, tuple[Tree[T], ...]]
type Forest[T: Hashable] = tuple[Tree[T], ...]


def t[T](
      value: T,
      *children: Tree[T],
) -> Tree[T]:
    """Small convenience function to help construct trees"""
    return value, children


def postorder[T](tree: Tree[T]) -> tuple[T, ...]:
    """A postorder traversal of the node data in ``tree``"""
    s1 = [tree]
    s2 = []
    while s1:
        current = s1.pop()
        s2.append(current[0])
        s1.extend(current[1])
    return tuple(reversed(s2))


def keyroots[T](tree: Tree[T]) -> tuple[int, ...]:
    """keyroot indices for keyroots in ``tree``"""
    s1 = [(True, tree)]
    s2 = []
    while s1:
        is_keyroot, current = s1.pop()
        s2.append(is_keyroot)
        _, children = current
        if children:
            s1.append((False, children[0]))
            s1.extend((True, children[i]) for i in range(1, len(children)))
    return tuple(i for i, is_key in enumerate(reversed(s2)) if is_key)


def leftmosts[T](tree: Tree[T]) -> tuple[int, ...]:
    """
    The postorder traversal of :math:`l(i)` for each index
    :math:`i` in :math:`T`
    """
    s1 = [tree]
    s2 = []
    while s1:
        current = s1.pop()
        s2.append(current)
        s1.extend(current[1])
    memo = {}
    indices = []
    for i, node in enumerate(reversed(s2)):
        if node[1]:
            child = node[1][0]
            index = memo[id(child)]
            memo[id(node)] = index
            indices.append(index)
        else:
            memo[id(node)] = i
            indices.append(i)
    return tuple(indices)