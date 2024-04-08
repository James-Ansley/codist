from ast import parse

from codist import t
from codist.ast import basic_ast, parse_ast_silhouette


def test_empty_code_is_parsed_to_a_module_silhouette():
    assert parse_ast_silhouette("") == ("Module", ())


def test_simple_expression_silhouette():
    assert parse_ast_silhouette("x = 1") == t(
        "Module",
        t("Assign", t("Name", t("Store")), t("Constant")),
    )


def test_basic_ast_makes_no_distinction_between_empty_literals_or_constructors():
    assert basic_ast(parse("[]", mode="eval"), {}) \
           == basic_ast(parse("list()", mode="eval"), {})
    assert basic_ast(parse("{}", mode="eval"), {}) \
           == basic_ast(parse("dict()", mode="eval"), {})
    assert basic_ast(parse("()", mode="eval"), {}) \
           == basic_ast(parse("tuple()", mode="eval"), {})


def test_basic_ast_reassigns_names():
    assert basic_ast(parse("x", mode="eval"), {"x": 1})[1][0][0] == "Name(1)"
