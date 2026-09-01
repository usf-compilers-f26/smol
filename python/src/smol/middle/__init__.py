"""Compiler middle end."""

from smol.middle.opt import optimize
from smol.middle.tir import (
    Arith,
    Block,
    Branch,
    Const,
    Copy,
    Exit,
    Instruction,
    Jump,
    Print,
    Program,
    Read,
    Terminator,
)

__all__ = [
    "Arith",
    "Block",
    "Branch",
    "Const",
    "Copy",
    "Exit",
    "Instruction",
    "Jump",
    "Print",
    "Program",
    "Read",
    "Terminator",
    "optimize",
]
