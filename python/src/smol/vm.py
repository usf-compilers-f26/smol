# Copyright (C) 2026 Mehmet Emre
# SPDX-License-Identifier: GPL-3.0-only
#
# This file is part of smol.
#
# smol is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3 as published by the Free
# Software Foundation.
#
# smol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# smol. If not, see <https://www.gnu.org/licenses/>.

"""Execute tiny IR programs with numeric input and output."""

from smol.front.ast import BOp
from smol.middle import tir


def _signed_64(value: int) -> int:
    return (value + (1 << 63)) % (1 << 64) - (1 << 63)


def _arith_64(op: BOp, left: int, right: int) -> int:
    match op:
        case BOp.ADD:
            result = left + right
        case BOp.SUB:
            result = left - right
        case BOp.MUL:
            result = left * right
        case BOp.DIV:
            if right == 0:
                result = -1
            else:
                quotient = abs(left) // abs(right)
                result = -quotient if (left < 0) != (right < 0) else quotient
        case BOp.LT:
            result = int(left < right)
    return _signed_64(result)


class VM:
    def __init__(self, program: tir.Program, inputs: list[int]) -> None:
        self.program = program
        self.inputs = list(inputs)
        self.outputs: list[int] = []
        self.env = dict.fromkeys(program.declarations, 0)

    def run(self) -> list[int]:
        label: str | None = "entry"
        while label is not None:
            label = self.run_bb(label)
        return self.outputs

    def run_bb(self, label: str) -> str | None:
        block = self.program.blocks[label]
        for instruction in block.instructions:
            self.run_inst(instruction)

        match block.terminator:
            case tir.Exit():
                return None
            case tir.Jump(next_label):
                return next_label
            case tir.Branch(guard, true_label, false_label):
                return true_label if self.env[guard] != 0 else false_label

    def run_inst(self, instruction: tir.Instruction) -> None:
        match instruction:
            case tir.Copy(dst, src):
                self.env[dst] = self.env[src]
            case tir.Const(dst, value):
                self.env[dst] = _signed_64(value)
            case tir.Arith(op, dst, lhs, rhs):
                self.env[dst] = _arith_64(op, self.env[lhs], self.env[rhs])
            case tir.Read(name):
                if not self.inputs:
                    raise ValueError("$read requires another input number")
                self.env[name] = _signed_64(self.inputs.pop(0))
            case tir.Print(name):
                self.outputs.append(self.env[name])


def run(program: tir.Program, inputs: list[int]) -> list[int]:
    """Run a tiny IR program and return its printed numbers."""
    return VM(program, inputs).run()
