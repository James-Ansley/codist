import ast

from .distance import Tree, tree

__all__ = ("parse_ast_silhouette", "ast_silhouette")


def parse_ast_silhouette(code: str) -> Tree[str]:
    """
    Parses the given code and returns a Tree containing only AST node type
    information.
    """
    return ast_silhouette(ast.parse(code))


def ast_silhouette(node: ast.AST) -> Tree[str]:
    """Returns a Tree containing only AST node type information"""
    return tree(
        type(node).__name__,
        tuple(ast_silhouette(n) for n in ast.iter_child_nodes(node))
    )
