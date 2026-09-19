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

from typing import Any

from smol.front.ast import (
    Assign,
    BinOp,
    BOp,
    Const,
    Expr,
    Negate,
    Print,
    Program,
    Stmt,
    Var,
)
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


class Inspector:
    indent: int = 0

    def __init__(self, name):
        self.name = name
        Inspector.pprint(f"parsing {name}")
        Inspector.indent += 2

    def __del__(self):
        Inspector.indent -= 2
        Inspector.pprint(f"parsed {self.name}")

    def pprint(s: Any, /, *args, **kwargs):
        """Print at the current indentation level."""
        print(f"{' ' * Inspector.indent}{s}", *args, **kwargs)


class Parser:
    def __init__(self, source: str) -> None:
        self.tokens = list(reversed(get_tokens(source)))

    def peek(self) -> Token | None:
        """Return the next token if there is one, don't pop it."""
        return self.tokens[-1] if self.tokens else None

    def next(self) -> Token:
        """Return and pop the next token."""
        t = self.peek()
        if t is None:
            raise ParseError("Reached the EOF too early.")
        Inspector.pprint(f"popped {self.tokens[-1]}")
        self.tokens.pop()
        return t

    def next_is(self, kind: TokenKind) -> bool:
        """Return whether the next token has the given kind."""
        t = self.peek()
        return t is not None and t.kind == kind

    def eat(self, kind: TokenKind) -> bool:
        """Consume the next token if it has the given kind."""
        if self.next_is(kind):
            self.next()  # just to pop the relevant token
            return True
        return False

    def expect(self, kind: TokenKind) -> Token:
        """Assert that the next token is of the given kind and consume it."""
        t = self.next()
        if t.kind != kind:
            raise ParseError(f"Expected a {kind}, got {t}.")
        return t

    def parse_program(self) -> Program:
        stmts = []
        while self.tokens:
            stmts.append(self.parse_stmt())
        return Program(stmts)

    def parse_stmt(self) -> Stmt:
        _dbg = Inspector("stmt")
        t = self.next()
        if t.kind == TokenKind.ASSIGN:
            lhs = self.expect(TokenKind.ID)
            rhs = self.parse_expr()
            return Assign(name=lhs.text, value=rhs)
        if t.kind == TokenKind.PRINT:
            return Print(self.parse_expr())
        if t.kind == TokenKind.READ:
            ...
        if t.kind == TokenKind.IF:
            ...
        raise ParseError(f"Expected the start of a statement, got {t}")

    def parse_block(self) -> tuple[Stmt, ...]:
        raise NotImplementedError("TODO: parse a block")

    def parse_expr(self) -> Expr:
        _dbg = Inspector("expr")
        if self.peek() in [TokenKind.ID, TokenKind.NUM, TokenKind.TILDE]:
            t = self.next()
            if t.kind == TokenKind.ID:
                return Var(name=t.text)
            if t.kind == TokenKind.NUM:
                return Const(value=int(t.text))
            if t.kind == TokenKind.TILDE:
                return Negate(self.parse_expr())

        # this must be a bop
        op = self.parse_bop()
        lhs = self.parse_expr()
        rhs = self.parse_expr()
        return BinOp(op, lhs, rhs)

    def parse_bop(self) -> BOp:
        _dbg = Inspector("bop")
        if self.eat(TokenKind.PLUS):
            return BOp.ADD
        self.expect(TokenKind.MUL)
        return BOp.MUL
