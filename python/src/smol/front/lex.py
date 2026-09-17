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

"""The regular-expression lexer."""

import re
from dataclasses import dataclass
from enum import StrEnum


class TokenKind(StrEnum):
    ID = "id"
    NUM = "num"
    ASSIGN = ":="
    PRINT = "$print"
    READ = "$read"
    IF = "$if"
    LBRACE = "{"
    RBRACE = "}"
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    LT = "<"
    TILDE = "~"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    text: str

    def __str__(self) -> str:
        return f"kind: '{self.kind}', part of input: '{self.text}'"


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        specifications = (
            (r"\$print", TokenKind.PRINT),
            (r"\$read", TokenKind.READ),
            (r"\$if", TokenKind.IF),
            (r"\{", TokenKind.LBRACE),
            (r"\}", TokenKind.RBRACE),
            (r":=", TokenKind.ASSIGN),
            (r"\+", TokenKind.PLUS),
            (r"-", TokenKind.MINUS),
            (r"\*", TokenKind.MUL),
            (r"/", TokenKind.DIV),
            (r"<", TokenKind.LT),
            (r"[a-zA-Z_][a-zA-Z0-9_]*", TokenKind.ID),
            (r"[0-9]+", TokenKind.NUM),
            (r"~", TokenKind.TILDE),
        )
        self._matchers = tuple(
            (re.compile(pattern), kind) for pattern, kind in specifications
        )
        self._whitespace = re.compile(r"(?:[ \t\f\r\n\v]|(?://.*))*")

    def end_of_input(self) -> bool:
        """Return whether all input has been consumed."""
        return self.pos == len(self.source)

    def skip_whitespace(self) -> None:
        """Skip whitespace and line comments."""
        if self.end_of_input():
            return
        match = self._whitespace.match(self.source, self.pos)
        if match:
            self.pos += len(match.group())

    def next(self) -> Token | None:
        """Return the next token, or None at end of input."""
        self.skip_whitespace()
        if self.end_of_input():
            return None

        matches = [
                (regex.match(self.source, self.pos), kind)
                for regex, kind in self._matchers
        ]

        matches = [
                (len(match.group()), kind, match.group())
                for match, kind in matches
                if match
        ]

        matches.sort(reverse=True)

        if matches != []:
            self.pos +=  matches[0][0]
            return Token(kind=matches[0][1], text=matches[0][2])

def get_tokens(source: str) -> list[Token]:
    lexer = Lexer(source)
    tokens: list[Token] = []
    while (token := lexer.next()) is not None:
        tokens.append(token)
    return tokens
