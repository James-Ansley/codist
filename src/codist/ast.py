"""
Utilities for converting abstract syntax trees to :data:`codist.tree.Tree`
objects
"""

import ast

from .tree import t, Tree

__all__ = ("parse_ast_silhouette", "ast_silhouette")


def parse_ast_silhouette(code: str) -> Tree[str]:
    """
    Parses the given code and returns a Tree containing only AST node type
    information.
    """
    return ast_silhouette(ast.parse(code))


def ast_silhouette(node: ast.AST) -> Tree[str]:
    """Returns a Tree containing only AST node type information"""
    return t(
        type(node).__name__,
        *(ast_silhouette(n) for n in ast.iter_child_nodes(node))
    )
