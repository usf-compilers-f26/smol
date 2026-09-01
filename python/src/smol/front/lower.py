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

"""Lowering from the AST to tiny IR."""

from dataclasses import dataclass

from smol.front import ast
from smol.middle import tir


@dataclass(frozen=True, slots=True)
class _Label:
    name: str


@dataclass(frozen=True, slots=True)
class _Inner:
    instruction: tir.Instruction


@dataclass(frozen=True, slots=True)
class _Term:
    terminator: tir.Terminator


type _TvEntry = _Label | _Inner | _Term


def lower(program: ast.Program) -> tir.Program:
    return _Lower().lower_program(program)


def construct_cfg(entries: list[_TvEntry]) -> dict[str, tir.Block]:
    """Convert a translation vector into a basic-block map."""
    del entries
    raise NotImplementedError("TODO: construct the control-flow graph")


class _Lower:
    def __init__(self) -> None:
        self.declarations: set[str] = set()
        self.translation: list[_TvEntry] = []
        self.fresh_counter = 0
        self.block_counter = 0

    def add_declaration(self, name: str) -> None:
        self.declarations.add(name)

    def lower_program(self, program: ast.Program) -> tir.Program:
        self.translation.append(_Label("entry"))
        for statement in program.statements:
            self.lower_stmt(statement)
        self.translation.append(_Term(tir.Exit()))
        return tir.Program(
            declarations=frozenset(self.declarations),
            blocks=construct_cfg(self.translation),
        )

    def lower_stmt(self, statement: ast.Stmt) -> None:
        del statement
        raise NotImplementedError("TODO: lower a statement")

    def lower_expr(self, expression: ast.Expr) -> str:
        del expression
        raise NotImplementedError("TODO: lower an expression")

    def mk_var(self, prefix: str) -> str:
        del prefix
        raise NotImplementedError("TODO: create a fresh variable")

    def mk_label(self) -> str:
        raise NotImplementedError("TODO: create a fresh basic-block label")
