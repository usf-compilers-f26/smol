# tiny IR

This document describes the intermediate representation our compiler uses for
optimizations.

## Syntax

tiny IR programs have the same set of identifiers and constants as smol
programs.  A tiny IR program is made up of a CFG that abides certain
constraints.

Here is the syntax for tiny IR programs:

```
// a program has some declared variables followed by the blocks.
program ::= id* ';' block*

// Informally:
//
// <block name>:
//   <instruction1>
//   ...
//   <instructionN>
//   <terminator>
block ::= id ':' insn* term

// Instructions
insn ::= '$copy' id id
       | '$const' id num
       | '$arith' bop id id
       | '$read' id
       | '$print' id
       
// Terminators
term ::= '$jump' id
       | '$branch' id id id
       | '$exit'
```

## Semantics

- All variables are initialized to zero.
- All I/O and arithmetic happens the way it is specified in the smol semantics
  document.

### Instructions

- `$arith op dst src1 src2`:  Update `dst` with `src1 op src2`.
- `$copy dst src`: Copy `src` to `dst`.
- `$const dst num`: Copy `num` to `dst`.
- `$read dst`: Read a number from the standard input and store it to `dst`.
- `$print src`: Print the number stored at `src` to the standard output.

### Terminators

These are instructions that end a basic block:

- `$jump b`: Jump to the basic block `b`.
- `$branch var tt ff`: Jump to `tt` if `var` is nonzero, jump to `ff` otherwise.
- `$exit`: Terminate the program.


## Well-formedness constraints

A tiny program has to conform the following constraints, otherwise it is
ill-formed.  The compiler must never generate ill-formed tiny IR programs:
- All variables must be declared.
- Each block's name must be unique.
- There must be one start block named `$entry`.
- There must be no cycles in the CFG.
