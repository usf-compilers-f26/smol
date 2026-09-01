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

"""Recursive-descent parser for smol's prefix grammar."""

from smol.front.ast import BOp, Expr, Program, Stmt
from smol.front.lex import Token, TokenKind, get_tokens


class ParseError(Exception):
    def __str__(self) -> str:
        return f"Parse error: {super().__str__()}"


def parse(source: str) -> Program:
    parser = Parser(source)
    program = parser.parse_program()
    if parser.tokens:
        raise ParseError(
            "There are still leftover tokens after reading a whole program."
        )
    return program


class Parser:
    def __init__(self, source: str) -> None:
        self.tokens = list(reversed(get_tokens(source)))

    def peek(self) -> Token | None:
        return self.tokens[-1] if self.tokens else None

    def next(self) -> Token:
        raise NotImplementedError("TODO: consume the next token")

    def next_is(self, kind: TokenKind) -> bool:
        raise NotImplementedError("TODO: test the next token's kind")

    def eat(self, kind: TokenKind) -> bool:
        raise NotImplementedError("TODO: optionally consume a token")

    def expect(self, kind: TokenKind) -> Token:
        raise NotImplementedError("TODO: consume a token of the expected kind")

    def parse_program(self) -> Program:
        raise NotImplementedError("TODO: parse a program")

    def parse_stmt(self) -> Stmt:
        raise NotImplementedError("TODO: parse a statement")

    def parse_block(self) -> tuple[Stmt, ...]:
        raise NotImplementedError("TODO: parse a block")

    def parse_expr(self) -> Expr:
        raise NotImplementedError("TODO: parse an expression")

    def parse_binop(self, op: BOp) -> Expr:
        raise NotImplementedError(f"TODO: parse both operands of {op}")
