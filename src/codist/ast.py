"""
Utilities for converting abstract syntax trees to :data:`codist.tree.Tree`
objects
"""

from ast import *
from collections.abc import Iterator

from .tree import Tree, t

__all__ = (
    "parse_ast_silhouette",
    "ast_silhouette",
    "parse_basic_ast",
    "basic_ast",
)
COLLECTION_FUNCS = ("list", "tuple", "set", "dict")


def is_reserved_name(name: str) -> bool:
    return name == "self" or name.startswith("__") and name.endswith("__")


def is_named_block_node(name: str) -> bool:
    return name.startswith("Function") or name.startswith("Class")


def parse_ast_silhouette(code: str) -> Tree[str]:
    """
    Parses the given code and returns a Tree containing only AST node type
    information.
    """
    return ast_silhouette(parse(code))


def ast_silhouette(node: AST) -> Tree[str]:
    """Returns a Tree containing only AST node type information"""
    return t(
        type(node).__name__,
        *(ast_silhouette(n) for n in iter_child_nodes(node))
    )


def nodes_of_type[T](
      node: AST,
      n_type: type[T],
) -> Iterator[T]:
    if isinstance(node, n_type):
        yield node
    for c in iter_child_nodes(node):
        yield from nodes_of_type(c, n_type)


def yield_names(node) -> Iterator[str]:
    match node:
        case (ClassDef(name)
              | FunctionDef(name)
              | arg(name)
              | Name(name)
              | Attribute(name)):
            yield name
    for child in iter_child_nodes(node):
        yield from yield_names(child)


def parse_basic_ast(code: str) -> Tree[str]:
    module = parse(code)
    # TODO — reorder function and class definitions by alphabetical
    #  order in the AST before processing names??
    names = dict.fromkeys((
        *(c.name for c in nodes_of_type(module, ClassDef)),
        *(f.name for f in nodes_of_type(module, FunctionDef)),
        *(a.arg for a in nodes_of_type(module, arg)),
        *(n.id for n in nodes_of_type(module, Name)),
        *(a.attr for a in nodes_of_type(module, Attribute)),
    ))
    names = (n for n in names if not is_reserved_name(n))
    name_map = {n: i for i, n in enumerate(names, start=1)}
    return basic_ast(module, name_map)


def basic_ast(node: AST, name_map: dict[str, int]) -> Tree[str]:
    """
    Returns a simplified abstract syntax tree that includes some name and
    constant information.

    Notes:
        * Makes no distinction between name contexts (e.g. Store/Load)
        * Marks 'self' and dunder methods as special names
        * Gives each non-special name a number in the rough order each
          of these items appear: Class, Function, Argument, Name, Attribute.
          That is, it will find all class names and mark them 1, 2, ...,
          and then the function names and number them continuing from the
          class names, etc.
        * Makes no distinction between empty literal collections vs empty
          collection constructors for lists, tuples, and dictionaries. I.e.
          ``[]`` is equivalent to ``list()``

    Caveats:
        * assumes builtin names are not overridden
        * assumes "self" is only used in class methods to refer to the
          class instance
        * assumes no non-standard dunder names are used
        * Removes type annotations on arguments
    """
    match node:
        case List() | Tuple() | Set() | Dict():
            return basic_collection(node, name_map)
        case Call(func=Name(id=f), args=[]) if f in COLLECTION_FUNCS:
            return basic_collection(node, name_map)
        case Name() | arg() | Attribute():
            return basic_name(node, name_map)
        case Constant(value):
            return t(f"Const({value!r})")
        case FunctionDef() | ClassDef():
            return basic_named_block(node, name_map)
        case _:
            return t(
                type(node).__name__,
                *(basic_ast(n, name_map) for n in iter_child_nodes(node)),
            )


def basic_named_block(node: AST, name_map) -> Tree[str]:
    match node:
        case FunctionDef(name):
            name = name if is_reserved_name(name) else name_map[name]
            return t(
                f"Function({name})",
                *(basic_ast(n, name_map) for n in iter_child_nodes(node)),
            )
        case ClassDef(name):
            name = name if is_reserved_name(name) else name_map[name]
            return t(
                f"Class({name})",
                *(basic_ast(n, name_map) for n in iter_child_nodes(node)),
            )
        case _:
            raise ValueError("Unrecognized AST block:", node)


def basic_name(node: AST, name_map) -> Tree[str]:
    match node:
        case Name(value) | arg(value) if is_reserved_name(value):
            return t(f"Name({value})")
        case Name(value) | arg(value):
            return t(f"Name({name_map[value]})")
        case Attribute(value, attr):
            name = attr if is_reserved_name(attr) else name_map[attr]
            return t(
                f"Attribute({name})",
                basic_ast(value, name_map),
            )
        case _:
            raise ValueError("Unrecognized AST name:", node)


def basic_collection(node: AST, name_map) -> Tree[str]:
    match node:
        case List([]) | Call(Name("list"), []):
            return t("List")
        case Tuple([]) | Call(Name("tuple"), []):
            return t("Tuple")
        case Set([]) | Call(Name("set"), []):
            return t("Set")
        case Dict([], []) | Call(Name("dict"), []):
            return t("Dict")
        case _:
            return t(
                type(node).__name__,
                *(basic_ast(n, name_map) for n in iter_child_nodes(node)),
            )
