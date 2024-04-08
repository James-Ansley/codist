from codist.tree import Lambda, keyroots, leftmosts, parents, postorder, t

tree1 = t("f", t("d", t("a"), t("c", t("b"))), t("e"))
tree2 = t("f", t("c", t("d", t("a"), t("b"))), t("e"))
tree3 = t(
    "g",
    t("e", t("a"), t("c", t("b")), t("d")),
    t("f"),
)
tree4 = t(
    "o",
    t("g", t("a"), t("c", t("b")), t("f", t("d"), t("e"))),
    t("n", t("i", t("h")), t("j"), t("k"), t("m", t("l"))),
)


def test_keyroots():
    assert keyroots(tree1) == (2, 4, 5)
    assert keyroots(tree2) == (1, 4, 5)
    assert keyroots(tree3) == (2, 3, 5, 6)
    assert keyroots(tree4) == (2, 4, 5, 9, 10, 12, 13, 14)


def test_postorder():
    assert postorder(tree1) == ("a", "b", "c", "d", "e", "f")
    assert postorder(tree2) == ("a", "b", "d", "c", "e", "f")
    assert postorder(tree3) == ("a", "b", "c", "d", "e", "f", "g")
    assert postorder(tree4) == ("a", "b", "c", "d", "e", "f", "g",
                                "h", "i", "j", "k", "l", "m", "n", "o")


def test_leftmost():
    assert leftmosts(tree1) == (0, 1, 1, 0, 4, 0)
    assert leftmosts(tree2) == (0, 1, 0, 0, 4, 0)
    assert leftmosts(tree3) == (0, 1, 1, 3, 0, 5, 0)
    assert leftmosts(tree4) == (0, 1, 1, 3, 4, 3, 0, 7, 7, 9, 10, 11, 11, 7, 0)


def test_parents():
    assert parents(tree1) == (3, 2, 3, 5, 5, Lambda)
    assert parents(tree2) == (2, 2, 3, 5, 5, Lambda)
    assert parents(tree3) == (4, 2, 4, 4, 6, 6, Lambda)
    assert parents(tree4) == (6, 2, 6, 5, 5, 6, 14, 8, 13,
                              13, 13, 12, 13, 14, Lambda)
