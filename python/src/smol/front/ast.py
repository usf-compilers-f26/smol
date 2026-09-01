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
