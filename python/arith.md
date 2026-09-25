# Arithmetic grammar

```
expr ::= expr bop1 term | term
bop1 ::= `+` | `-`

term ::= term bop2 factor | factor
bop2 ::= `*` | `/`

factor ::= `{` expr `}` | num | id
```

Examples:
- x + 3 * y
  -> x + (3 * y)
- 3 - 4 - 5
  -> (3 - 4) - 5

# After left refactoring

```
--- expr ::= term (bop1 term)*
---
--- or
---
--- expr ::= (term bop1)* term

expr ::= term expr'
expr' ::= bop1 term expr' | _


expr ::= term (bop1 expr)?

bop1 ::= `+` | `-`

term ::= factor term'
term' ::= (bop2 factor)* term' | _
bop2 ::= `*` | `/`

factor ::= `{` expr `}` | num | id
```

acc := x
-> read - y
acc := acc - y = x - y
-> read - z
acc := acc - z = (x - y) - z

x - y - z

Right-associative -> Recursion
Left-associative  -> Loop


