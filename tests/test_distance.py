from codist import t
from codist.distance import Cost, Lambda, tree_dist, tree_edit

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
tree5 = t(
        "d",
        t("b", t("a"), t("c")),
        t("f", t("e"), t("g")),

    )
tree6 = t("f", t("e", t("x")), t("g"))


def test_two_identical_trees_have_an_edit_distance_of_zero():
    assert tree_dist(t("a"), t("a")) == 0
    assert tree_dist(t("a", t("b")), t("a", t("b"))) == 0
    assert tree_dist(
        t("a", t("b"), t("c")),
        t("a", t("b"), t("c")),
    ) == 0


def test_relabeling_a_single_node_will_cost_one_relabel():
    assert tree_dist(t("a"), t("b")) == 1
    cost = Cost(
        relabel=lambda n1, n2: 10,
        insert=lambda n: 100,
        delete=lambda n: 100,
    )
    assert tree_dist(t("a"), t("b"), cost) == 10
    assert tree_dist(t("a"), t("b"), Cost(insert=lambda n: 10)) == 1


def test_tree_edit_distance_will_find_the_minimum_edit_distance():
    cost = Cost(
        delete=(lambda _: 3),
        insert=(lambda _: 3),
        relabel=(lambda n1, n2: 0 if n1 == n2 else 2),
    )
    # Delete d, b, a, c; Insert x
    assert tree_dist(tree5, tree6, cost) == 15
    assert tree_dist(tree6, tree5, cost) == 15
    cost = Cost(
        delete=(lambda _: 3),
        insert=(lambda _: 3),
        relabel=(lambda n1, n2: 2),
    )
    # Delete c, e, g; Relabel f -> g, d -> f, b -> e, a -> x
    assert tree_dist(tree5, tree6, cost) == 17
    assert tree_dist(tree6, tree5, cost) == 17


def test_tree_dist():
    assert tree_dist(tree1, tree1) == 0
    assert tree_dist(tree1, tree2) == 2
    assert tree_dist(tree1, tree3) == 4
    assert tree_dist(tree1, tree4) == 12
    assert tree_dist(tree2, tree2) == 0
    assert tree_dist(tree2, tree3) == 6
    assert tree_dist(tree2, tree4) == 14
    assert tree_dist(tree3, tree3) == 0
    assert tree_dist(tree3, tree4) == 11
    assert tree_dist(tree4, tree4) == 0

    assert tree_dist(tree2, tree1) == 2
    assert tree_dist(tree3, tree1) == 4
    assert tree_dist(tree4, tree1) == 12
    assert tree_dist(tree3, tree2) == 6
    assert tree_dist(tree4, tree2) == 14
    assert tree_dist(tree4, tree3) == 11

    cost = Cost(
        delete=(lambda _: 10),
        insert=(lambda _: 10),
        relabel=(lambda n1, n2: 0 if n1 == n2 else 10),
    )
    assert tree_dist(tree1, tree2, cost) == 20
    assert tree_dist(tree2, tree1, cost) == 20


def test_tree_edit_path_will_return_operations_to_transform_one_tree_into_another():
    cost = Cost(
        delete=(lambda _: 3),
        insert=(lambda _: 3),
        relabel=(lambda n1, n2: 0 if n1 == n2 else 2),
    )
    # Delete d, b, a, c; Insert x
    cost, path = tree_edit(tree5, tree6, cost)
    assert cost == 15
    assert set(path) == {
        ("d", Lambda, 6), ("b", Lambda, 2), ("a", Lambda, 0), ("c", Lambda, 1),
        (Lambda, "x", 1), ('e', 'e', 3), ('f', 'f', 5), ('g', 'g', 4),
    }
    cost = Cost(
        delete=(lambda _: 3),
        insert=(lambda _: 3),
        relabel=(lambda n1, n2: 2),
    )
    # Delete c, e, g; Relabel f -> g, d -> f, b -> e, a -> x
    cost, path = tree_edit(tree5, tree6, cost)
    assert cost == 17
    assert set(path) == {
        ("c", Lambda, 1), ("f", Lambda, 5), ("g", Lambda, 4),
        ("e", "g", 3), ("d", "f", 6), ("b", "e", 2), ("a", "x", 0)
    }
