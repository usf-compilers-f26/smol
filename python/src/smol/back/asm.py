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

"""The 64-bit RISC-V (RV64G) assembly model."""

from dataclasses import dataclass
from enum import StrEnum

WORD_SIZE = 8
LOG2_WORD_SIZE = 3
GC_INIT_FN = "_cflat_init_gc"
ALLOC_FN = "_cflat_alloc"


class Register(StrEnum):
    ZERO = "zero"
    RA = "ra"
    SP = "sp"
    GP = "gp"
    TP = "tp"
    T0 = "t0"
    T1 = "t1"
    T2 = "t2"
    FP = "fp"
    S1 = "s1"
    A0 = "a0"
    A1 = "a1"
    A2 = "a2"
    A3 = "a3"
    A4 = "a4"
    A5 = "a5"
    A6 = "a6"
    A7 = "a7"
    S2 = "s2"
    S3 = "s3"
    S4 = "s4"
    S5 = "s5"
    S6 = "s6"
    S7 = "s7"
    S8 = "s8"
    S9 = "s9"
    S10 = "s10"
    S11 = "s11"
    T3 = "t3"
    T4 = "t4"
    T5 = "t5"
    T6 = "t6"


ARG_REGISTERS = (
    Register.A0,
    Register.A1,
    Register.A2,
    Register.A3,
    Register.A4,
    Register.A5,
    Register.A6,
    Register.A7,
)


class ArithOp(StrEnum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    SLT = "slt"
    AND = "and"
    OR = "or"
    XOR = "xor"
    SRL = "srl"
    SRA = "sra"
    SLL = "sll"


class Condition(StrEnum):
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    LESS = "lt"
    LESS_EQUAL = "le"
    GREATER = "gt"
    GREATER_EQUAL = "ge"


@dataclass(frozen=True, slots=True)
class Memory:
    base: Register
    offset: int = 0

    def __str__(self) -> str:
        return f"{self.offset}({self.base})"

    def with_offset(self, offset: int) -> Memory:
        return Memory(self.base, self.offset + offset)

    def used_register(self) -> Register:
        return self.base


@dataclass(frozen=True, slots=True)
class Global:
    index: int
    offset: int = 0

    def __str__(self) -> str:
        return f"{self.offset}(global#{self.index})"

    def with_offset(self, offset: int) -> Global:
        return Global(self.index, self.offset + offset)

    def used_register(self) -> None:
        return None


type MemoryLocation = Memory | Global


@dataclass(frozen=True, slots=True)
class MemoryL:
    memory: MemoryLocation

    def used_register(self) -> Register | None:
        return self.memory.used_register()

    def get_memory(self) -> MemoryLocation:
        return self.memory

    def with_offset(self, offset: int) -> MemoryL:
        return MemoryL(self.memory.with_offset(offset))


@dataclass(frozen=True, slots=True)
class Reg:
    register: Register

    def used_register(self) -> Register:
        return self.register

    def get_memory(self) -> None:
        return None

    def with_offset(self, offset: int) -> Reg:
        if offset != 0:
            message = "internal error: tried to take non-zero offset from a register"
            raise ValueError(message)
        return self


type Location = MemoryL | Reg


@dataclass(frozen=True, slots=True)
class LocalTarget:
    name: str


@dataclass(frozen=True, slots=True)
class GlobalTarget:
    name: str


type JumpTarget = LocalTarget | GlobalTarget


@dataclass(frozen=True, slots=True)
class La:
    dst: Register
    src: MemoryLocation

    def __str__(self) -> str:
        return f"la {self.dst}, {self.src}"


@dataclass(frozen=True, slots=True)
class Ld:
    dst: Register
    src: MemoryLocation

    def __str__(self) -> str:
        return f"ld {self.dst}, {self.src}"


@dataclass(frozen=True, slots=True)
class Sd:
    dst: MemoryLocation
    src: Register

    def __str__(self) -> str:
        return f"sd {self.src}, {self.dst}"


@dataclass(frozen=True, slots=True)
class Li:
    dst: Register
    immediate: int

    def __str__(self) -> str:
        return f"li {self.dst}, {self.immediate}"


@dataclass(frozen=True, slots=True)
class Arith:
    op: ArithOp
    dst: Register
    lhs: Register
    rhs: Register

    def __str__(self) -> str:
        return f"{self.op} {self.dst}, {self.lhs}, {self.rhs}"


@dataclass(frozen=True, slots=True)
class ArithI:
    op: ArithOp
    dst: Register
    lhs: Register
    rhs: int

    def __str__(self) -> str:
        return f"{self.op}i {self.dst}, {self.lhs}, {self.rhs}"


@dataclass(frozen=True, slots=True)
class Jal:
    dst: Register
    target: JumpTarget

    def __str__(self) -> str:
        return f"jal {self.dst}, {_target_text(self.target)}"


@dataclass(frozen=True, slots=True)
class Jalr:
    dst: Register
    target: Register

    def __str__(self) -> str:
        return f"jalr {self.dst}, {self.target}"


@dataclass(frozen=True, slots=True)
class Branch:
    condition: Condition
    lhs: Register
    rhs: Register
    target: JumpTarget

    def __str__(self) -> str:
        return f"b{self.condition} {self.lhs}, {self.rhs}, {_target_text(self.target)}"


@dataclass(frozen=True, slots=True)
class CompareZero:
    dst: Register
    lhs: Register
    condition: Condition

    def __str__(self) -> str:
        return f"s{self.condition}z {self.dst}, {self.lhs}"


@dataclass(frozen=True, slots=True)
class Comment:
    text: str

    def __str__(self) -> str:
        return f"# {self.text!r}"


type Instruction = (
    La | Ld | Sd | Li | Arith | ArithI | Jal | Jalr | Branch | CompareZero | Comment
)


def _target_text(target: JumpTarget) -> str:
    if isinstance(target, LocalTarget):
        return f"{target.name} # local, basic block"
    return f"{target.name} # global, function"


def used_registers(instruction: Instruction) -> tuple[Register, ...]:
    """Return all registers mentioned by an instruction."""
    match instruction:
        case La(dst, src) | Ld(dst, src):
            base = src.used_register()
            return (dst,) if base is None else (dst, base)
        case Sd(dst, src):
            base = dst.used_register()
            return (src,) if base is None else (base, src)
        case Arith(_, dst, lhs, rhs):
            return (dst, lhs, rhs)
        case ArithI(_, dst, lhs, _):
            return (dst, lhs)
        case Li(dst, _):
            return (dst,)
        case Jalr(dst, target):
            return (target, dst)
        case Jal(dst, _):
            return (dst,)
        case Branch(_, lhs, rhs, _):
            return (lhs, rhs)
        case CompareZero(dst, lhs, _):
            return (lhs, dst)
        case Comment(_):
            return ()


def jump(target: JumpTarget) -> Jal:
    """Create a jump that does not save a return address."""
    return Jal(Register.ZERO, target)


def call(callee: str) -> Jal:
    """Create a direct call using the ABI return-address register."""
    return Jal(Register.RA, GlobalTarget(callee))


def mov(dst: Register, src: Register) -> ArithI:
    """Move a value between registers using add-immediate zero."""
    return ArithI(ArithOp.ADD, dst, src, 0)


def read(dst: Register, src: Location) -> Instruction:
    """Load a location, using a move when it is already a register."""
    if isinstance(src, Reg):
        return mov(dst, src.register)
    return Ld(dst, src.memory)


def write(dst: Location, src: Register) -> Instruction:
    """Store to a location, using a move when it is a register."""
    if isinstance(dst, Reg):
        return mov(dst.register, src)
    return Sd(dst.memory, src)


@dataclass(frozen=True, slots=True)
class BasicBlock:
    name: str
    instructions: tuple[Instruction, ...]


@dataclass(frozen=True, slots=True)
class Program:
    name: str
    basic_blocks: dict[str, BasicBlock]
    stack_space: int
    used_registers: tuple[Register, ...]

    def asm_code(self) -> str:
        raise NotImplementedError("TODO: generate the final assembly code")
