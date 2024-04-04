# CoDist

CoDist (Code Distance) is a library that provides functions to calculate the
edit distance and edit paths of abstract syntax trees.

While this library is primarily concerned with AST edit distances, it can handle
any generic tree of the form: `Tree[T] = tuple[T, tuple[Tree[T], ...]]`

## Install

```
pip install codist
```

## Usage

Currently, only AST node _type_ information is compared. A silhouette of an AST
(an AST containing only type information) is constructed with
the `parse_ast_silhouette` function.

```python
from pprint import pprint
from codist.ast import parse_ast_silhouette

code1 = """
def process(data):
    result = []
    for x in data:
        if x > 5:
            result.append(x)
    return result
"""

code2 = """
def process(data):
    result = []
    for x in data:
        if x >= 6:
            result += [x]
    return result
"""

ast1 = parse_ast_silhouette(code1)
ast2 = parse_ast_silhouette(code2)

pprint(ast1)
pprint(ast2)
```

Which prints:

```
('Module',
 (('FunctionDef',
   (('arguments', (('arg', ()),)),
    ('Assign', (('Name', (('Store', ()),)), ('List', (('Load', ()),)))),
    ('For',
     (('Name', (('Store', ()),)),
      ('Name', (('Load', ()),)),
      ('If',
       (('Compare', (('Name', (('Load', ()),)), ('Gt', ()), ('Constant', ()))),
        ('Expr',
         (('Call',
           (('Attribute', (('Name', (('Load', ()),)), ('Load', ()))),
            ('Name', (('Load', ()),)))),)))))),
    ('Return', (('Name', (('Load', ()),)),)))),))
('Module',
 (('FunctionDef',
   (('arguments', (('arg', ()),)),
    ('Assign', (('Name', (('Store', ()),)), ('List', (('Load', ()),)))),
    ('For',
     (('Name', (('Store', ()),)),
      ('Name', (('Load', ()),)),
      ('If',
       (('Compare', (('Name', (('Load', ()),)), ('GtE', ()), ('Constant', ()))),
        ('AugAssign',
         (('Name', (('Store', ()),)),
          ('Add', ()),
          ('List', (('Name', (('Load', ()),)), ('Load', ()))))))))),
    ('Return', (('Name', (('Load', ()),)),)))),))
```

The distance between two ASTs can be computed with the `tree_dist` function.

```python
from codist import tree_dist

print("The above trees have a distance of:", tree_dist(ast1, ast2))
```

Would print:

```text
The above trees have a distance of: 8
```

The edit path and distance between two trees can be computed with
the `tree_edit` function. For convenience, this function also computes the
edit distance:

```python
from codist import tree_edit

dist, path = tree_edit(ast1, ast2)
print("The above trees have a distance of:", dist)
print("And an edit path of:")
pprint(tuple(e for e in path if e[0] != e[1]))
```

which prints:


```
The above trees have a distance of: 8
And an edit path of:
(('Gt', 'GtE'),
 ('Load', 'Store'),
 ('Load', 'Add'),
 ('Attribute', 'Λ'),
 ('Λ', 'Load'),
 ('Λ', 'List'),
 ('Call', 'AugAssign'),
 ('Expr', 'Λ'))
```

A custom set of `Cost` functions can be provided to change the weights of
insertions, deletions, and relabelings. By default, all change operations are 1
except for the case of γ(a -> a) which is 0. To change the cost, construct
a `Cost` object:

```python
from codist import Cost

cost = Cost(
    delete=(lambda n: 3),
    insert=(lambda n: 3),
    relabel=(lambda n1, n2: 0 if n1 == n2 else 2),
)

dist = tree_dist(ast1, ast2, cost=cost)

print("The above trees have a distance of:", dist)
```

Which prints:

```
The above trees have a distance of: 20
```
