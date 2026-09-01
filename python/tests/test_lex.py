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

import pytest

from smol.front.lex import Lexer, Token, TokenKind, get_tokens


def token(kind: TokenKind, text: str | None = None) -> Token:
    return Token(kind, text if text is not None else kind.value)


def test_skip_whitespace() -> None:
    lexer = Lexer("foo")
    lexer.skip_whitespace()
    assert lexer.pos == 0
    lexer = Lexer(" \n\t  foo")
    lexer.skip_whitespace()
    assert lexer.pos == 5
    lexer = Lexer(" // stuff\n\t  foo ")
    lexer.skip_whitespace()
    assert lexer.pos == 13


def test_empty() -> None:
    assert get_tokens("") == []
    assert get_tokens("  \n//hello\n") == []
    assert get_tokens("  \n//hi") == []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x", token(TokenKind.ID, "x")),
        ("print", token(TokenKind.ID, "print")),
        ("if", token(TokenKind.ID, "if")),
        ("yolo", token(TokenKind.ID, "yolo")),
        ("3", token(TokenKind.NUM, "3")),
        ("0345678910", token(TokenKind.NUM, "0345678910")),
        ("%", token(TokenKind.ERROR, "%")),
        *[
            (kind.value, token(kind))
            for kind in TokenKind
            if kind not in {TokenKind.ID, TokenKind.NUM, TokenKind.ERROR}
        ],
    ],
)
def test_single_token(source: str, expected: Token) -> None:
    assert get_tokens(source) == [expected]


def test_multi_token() -> None:
    assert get_tokens("x$print$read$if{}+0-*$/<") == [
        token(TokenKind.ID, "x"),
        token(TokenKind.PRINT),
        token(TokenKind.READ),
        token(TokenKind.IF),
        token(TokenKind.LBRACE),
        token(TokenKind.RBRACE),
        token(TokenKind.PLUS),
        token(TokenKind.NUM, "0"),
        token(TokenKind.MINUS),
        token(TokenKind.MUL),
        token(TokenKind.ERROR, "$"),
        token(TokenKind.DIV),
        token(TokenKind.LT),
    ]
    assert get_tokens("x yz $print $read $if { } +  0   -  //hi\n * $ read / < ~") == [
        token(TokenKind.ID, "x"),
        token(TokenKind.ID, "yz"),
        token(TokenKind.PRINT),
        token(TokenKind.READ),
        token(TokenKind.IF),
        token(TokenKind.LBRACE),
        token(TokenKind.RBRACE),
        token(TokenKind.PLUS),
        token(TokenKind.NUM, "0"),
        token(TokenKind.MINUS),
        token(TokenKind.MUL),
        token(TokenKind.ERROR, "$"),
        token(TokenKind.ID, "read"),
        token(TokenKind.DIV),
        token(TokenKind.LT),
        token(TokenKind.TILDE),
    ]
