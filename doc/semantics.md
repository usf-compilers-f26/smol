# smol semantics

Here are some notes about the semantics of smol:

# Scope and variables
- All variables have global scope.
- Variables are not declared, the compiler finds all the variables that are
  used, and allocates space for them.
- All variables are 64-bit integers.
- All variables are initialized to 0.

# Arithmetic
Arithmetic works the way it does on 64-bit RISC-V:

- All arithmetic is done over 64-bit signed integers using 2's complement.
- Division by zero results in `-1`.

# I/O

- `$read` and `$print` treat their arguments as 64-bit signed integers using 2's
  complement.  These values are read and written as decimals.

# Conditionals

- A `$if` statement evaluates the guard, and:
    - It takes the true branch if the guard is non-zero.
    - It takes the false branch if the guard is zero.
