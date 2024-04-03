from codist.distance import Cost, forest_dist, tree, tree_dist


def test_two_empty_trees_have_an_edit_distance_of_zero():
    assert tree_dist((), ()) == 0


def test_two_empty_forests_have_an_edit_distance_of_zero():
    assert forest_dist((), ()) == 0


def test_two_identical_trees_have_an_edit_distance_of_zero():
    assert tree_dist(tree("a"), tree("a")) == 0
    assert tree_dist(tree("a", (tree("b"),)), tree("a", (tree("b"),))) == 0
    assert tree_dist(
        tree("a", (tree("b"), tree("c"))),
        tree("a", (tree("b"), tree("c"))),
    ) == 0


def test_two_identical_forests_have_an_edit_distance_of_zero():
    f1 = (tree("a"),)
    f2 = (tree("a"), tree("b"))
    f3 = (tree("a", (tree("b"),)), tree("c"))
    assert forest_dist(f1, f1) == 0
    assert forest_dist(f2, f2) == 0
    assert forest_dist(f3, f3) == 0


def test_inserting_a_single_node_will_cost_one_insertion():
    assert tree_dist((), tree("a")) == 1
    assert tree_dist((), tree("a"), Cost(insert=lambda n: 10)) == 10
    assert tree_dist((), tree("a"), Cost(delete=lambda n: 10)) == 1


def test_deleting_a_single_node_will_cost_one_deletion():
    assert tree_dist(tree("a"), ()) == 1
    assert tree_dist(tree("a"), (), Cost(delete=lambda n: 10)) == 10
    assert tree_dist(tree("a"), (), Cost(insert=lambda n: 10)) == 1


def test_relabeling_a_single_node_will_cost_one_relabel():
    assert tree_dist(tree("a"), tree("b")) == 1
    cost = Cost(
        relabel=lambda n1, n2: 10,
        insert=lambda n: 100,
        delete=lambda n: 100,
    )
    assert tree_dist(tree("a"), tree("b"), cost) == 10
    assert tree_dist(tree("a"), tree("b"), Cost(insert=lambda n: 10)) == 1


def test_tree_edit_distance_will_find_the_minimum_edit_distance():
    tree1 = tree(
        "d",
        (
            tree("b", (tree("a"), tree("c"))),
            tree("f", (tree("e"), tree("g"))),
        ),
    )
    tree2 = tree("f", (tree("e", (tree("x"),)), tree("g")))
    cost = Cost(
        delete=(lambda _: 3),
        insert=(lambda _: 3),
        relabel=(lambda n1, n2: 0 if n1 == n2 else 2),
    )
    # Delete d, b, a, c; Insert x
    assert tree_dist(tree1, tree2, cost) == 15
    assert tree_dist(tree2, tree1, cost) == 15
    cost = Cost(
        delete=(lambda _: 3),
        insert=(lambda _: 3),
        relabel=(lambda n1, n2: 2),
    )
    # Delete c, e, g; Relabel f -> g, d -> f, b -> e, a -> x
    assert tree_dist(tree1, tree2, cost) == 17
    assert tree_dist(tree2, tree1, cost) == 17
