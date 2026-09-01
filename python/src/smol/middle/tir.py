"""The tiny intermediate representation."""

from dataclasses import dataclass

from smol.front.ast import BOp


@dataclass(frozen=True, slots=True)
class Copy:
    dst: str
    src: str

    def __str__(self) -> str:
        return f"{self.dst} = $copy {self.src}"


@dataclass(frozen=True, slots=True)
class Const:
    dst: str
    src: int

    def __str__(self) -> str:
        return f"{self.dst} = $const {self.src}"


@dataclass(frozen=True, slots=True)
class Arith:
    op: BOp
    dst: str
    lhs: str
    rhs: str

    def __str__(self) -> str:
        return f"{self.dst} = $arith {self.op} {self.lhs} {self.rhs}"


@dataclass(frozen=True, slots=True)
class Read:
    name: str

    def __str__(self) -> str:
        return f"$read {self.name}"


@dataclass(frozen=True, slots=True)
class Print:
    name: str

    def __str__(self) -> str:
        return f"$print {self.name}"


type Instruction = Copy | Const | Arith | Read | Print


@dataclass(frozen=True, slots=True)
class Exit:
    def __str__(self) -> str:
        return "$exit"


@dataclass(frozen=True, slots=True)
class Jump:
    label: str

    def __str__(self) -> str:
        return f"$jump {self.label}"


@dataclass(frozen=True, slots=True)
class Branch:
    guard: str
    true_label: str
    false_label: str

    def __str__(self) -> str:
        return f"$branch {self.guard} {self.true_label} {self.false_label}"


type Terminator = Exit | Jump | Branch


@dataclass(frozen=True, slots=True)
class Block:
    instructions: tuple[Instruction, ...]
    terminator: Terminator


@dataclass(frozen=True, slots=True)
class Program:
    declarations: frozenset[str]
    blocks: dict[str, Block]

    def __str__(self) -> str:
        lines = ["let " + "".join(f"{name}, " for name in sorted(self.declarations))]
        for label in sorted(self.blocks):
            block = self.blocks[label]
            lines.append(f"{label}:")
            lines.extend(f"    {instruction}" for instruction in block.instructions)
            lines.append(f"    {block.terminator}")
        return "\n".join(lines) + "\n"
