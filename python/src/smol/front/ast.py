"""The abstract syntax tree."""

from dataclasses import dataclass
from enum import StrEnum


class BOp(StrEnum):
    MUL = "mul"
    DIV = "div"
    ADD = "add"
    SUB = "sub"
    LT = "lt"


@dataclass(frozen=True, slots=True)
class Var:
    name: str


@dataclass(frozen=True, slots=True)
class Const:
    value: int


@dataclass(frozen=True, slots=True)
class BinOp:
    op: BOp
    lhs: Expr
    rhs: Expr


@dataclass(frozen=True, slots=True)
class Negate:
    inner: Expr


type Expr = Var | Const | BinOp | Negate


@dataclass(frozen=True, slots=True)
class Assign:
    name: str
    value: Expr


@dataclass(frozen=True, slots=True)
class Print:
    value: Expr


@dataclass(frozen=True, slots=True)
class Read:
    name: str


@dataclass(frozen=True, slots=True)
class If:
    guard: Expr
    true_branch: tuple[Stmt, ...]
    false_branch: tuple[Stmt, ...]


type Stmt = Assign | Print | Read | If


@dataclass(frozen=True, slots=True)
class Program:
    statements: tuple[Stmt, ...]
