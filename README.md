# smol - A small programming language and compiler

This repository contains the compiler for a small language that we will develop
through in-class exercises in CS 414 at University of San Francisco.  This
compiler will contain examples of all modules except garbage collection and
register allocation.

## Specification

- See `doc/syntax.md` for the syntax.
- See `doc/ir.md` for the IR.
- See `doc/semantics.md` for the semantics.

## Architecture of the compiler

We have a fairly traditional compiler architecture that looks like the following:

```
source code --[lex]--> tokens --[parse]--> AST --[lower]--> IR --[optimize]--> optimized IR
                                                                                    | 
                                                                               [code gen] 
                                                                                    | 
                                                                                    v 
                                                                               riscv asm 
                                                                                    | 
                                                                         [assembler and linker] 
                                                                                    | 
                                                                                    v 
                                                                            riscv executable
```

Here is where everything is found:

TODO

## Libraries we are using

We use the following Rust crates both in the full CFlat compiler and in this compiler:
- [`internment`](https://crates.io/crates/internment) is used for interning
  strings like identifiers, thus making them cheap to copy around.  This is a
  crucial optimization that separates a glacially slow compiler from a decent
  one.
  - To keep our implementation simple, we use the `Intern` type, which **never
    frees these strings**.  That is usually OK for our compiler: we intern
    variable, block and function names which need to live until almost the end,
    and never freeing allows copies to be effectively free.  We could have used
    `ArcIntern` or `ArenaIntern` for better memory management.
- [`regex`](https://crates.io/crates/regex) for using regular expressions when
  implementing our lexer.
- [`clap`](https://crates.io/crates/clap) for command-line argument parsing.
- [`derive_more`](https://crates.io/crates/derive_more) for deriving some traits
  semi-automatically so we write less code.

You will need to interact with only the first two, and `internment` will be
mostly transparent to us when building the compiler.

## Running the compiler

You can run the compiler via `cargo run -- [-O] [-o type] <input file>`.  It
prints its output to stdout.

The input file has to be a smol program.

The output file type can be one of:
- `tokens`: Token sequence.  For testing the lexer.
- `ast`: Abstract syntax tree.  For testing the parser.
- `tir`: Tiny IR.  For testing the lowerer.
- `asm`: Assembly program.  For testing the whole compiler.

The default output type is the assembly program.

`-O` flag enables optimizations.  It is disabled by default.

## Running the VM

This compiler comes with a VM for its IR so that we can run the output of the
front-end + the middle-end without a back-end for testing.  Run the VM via

```
cargo run --bin vm -- <tir program>
```

## Running the tests

Run `cargo test` to run all the tests.  You can specify a "test name" (a
substring).  For example, `cargo test foo` will run only the tests that contain
the string `foo` in their name.
