"""RISC-V code generation."""

from smol.back import asm
from smol.middle import tir


def code_gen(program: tir.Program) -> asm.Program:
    del program
    raise NotImplementedError("TODO: generate RISC-V assembly")
