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

"""Parse a smol program from a file or standard input and print its AST."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from smol.front.ast import (
    BinOp,
    BOp,
    Const,
    Expr,
    Negate,
    Var,
)
from smol.front.lex import Token, TokenKind, get_tokens


class ParseError(Exception):
    def __str__(self) -> str:
        return f"Parse error: {super().__str__()}"


def parse(source: str) -> Expr:
    parser = Parser(source)
    program = parser.parse_expr()
    if parser.tokens:
        raise ParseError(
            "There are still leftover tokens after reading a whole program."
        )
    return program


_DEBUG = True


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
        if _DEBUG:
            print(f"{' ' * Inspector.indent}{s}", *args, **kwargs)


_BINOP_MAP = {
    TokenKind.MUL: BOp.MUL,
    TokenKind.DIV: BOp.DIV,
    TokenKind.PLUS: BOp.ADD,
    TokenKind.MINUS: BOp.SUB,
    TokenKind.LT: BOp.LT,
}


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

    def parse_expr(self) -> Expr:
        _dbg = Inspector("expr")
        lhs = self.parse_term()

        while True:
            op = None
            if self.eat(TokenKind.PLUS):
                op = BOp.ADD
            elif self.eat(TokenKind.MINUS):
                op = BOp.SUB
            if op is None:
                return lhs

            rhs = self.parse_term()
            lhs = BinOp(op, lhs, rhs)

    def parse_term(self) -> Expr:
        _dbg = Inspector("term")
        lhs = self.parse_factor()

        while True:
            op = None
            if self.eat(TokenKind.MUL):
                op = BOp.MUL
            elif self.eat(TokenKind.DIV):
                op = BOp.DIV

            if not op:
                return lhs
            rhs = self.parse_factor()
            lhs = BinOp(op, lhs, rhs)

    def parse_factor(self) -> Expr:
        _dbg = Inspector("term")
        t = self.next()
        match t.kind:
            case TokenKind.LBRACE:
                inner = self.parse_expr()
                self.expect(TokenKind.RBRACE)
                return inner
            case TokenKind.NUM:
                return Const(int(t.text))
            case TokenKind.ID:
                return Var(t.text)

        raise ParseError(f"Expected brace, number, or variable name. Got {t}")

def pretty(e: Expr) -> str:
    match e:
        case Var(name):
            return name
        case Const(value):
            return str(value)
        case Negate(e):
            return f"(- {pretty(e)})"
        case BinOp(op, lhs, rhs):
            return f"({pretty(lhs)} {op} {pretty(rhs)})"


def main(argv: Sequence[str] | None = None) -> None:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument(
        "file", nargs="?", type=Path, help="input file (default: stdin)"
    )
    args = argument_parser.parse_args(argv)
    try:
        source = (
            args.file.read_text(encoding="utf-8")
            if args.file is not None
            else sys.stdin.read()
        )
        print(pretty(parse(source)))
    except (OSError, UnicodeError, ParseError) as error:
        argument_parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
