from codist.ast import parse_ast_silhouette
from codist import t


def test_empty_code_is_parsed_to_a_module_silhouette():
    assert parse_ast_silhouette("") == ("Module", ())


def test_simple_expression_silhouette():
    assert parse_ast_silhouette("x = 1") == t(
        "Module",
        t("Assign", t("Name", t("Store")), t("Constant")),
    )
