from codist.ast import parse_ast_silhouette
from codist.distance import tree


def test_empty_code_is_parsed_to_a_module_silhouette():
    assert parse_ast_silhouette("") == ("Module", ())


def test_simple_expression_silhouette():
    assert parse_ast_silhouette("x = 1") == tree(
        "Module",
        (
            tree(
                "Assign",
                (tree("Name", (tree("Store"),)), tree("Constant"))
            ),
        )
    )
