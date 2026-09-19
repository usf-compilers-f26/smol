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

from smol.front.parse import ParseError, parse


@pytest.mark.parametrize("source", ["x", "0", "<", ":= x y + z", ":= x y + z t"])
def test_invalid_program(source: str) -> None:
    with pytest.raises(ParseError):
        parse(source)


def test_invalid_print() -> None:
    with pytest.raises(ParseError):
        parse("$print")


def test_invalid_read() -> None:
    with pytest.raises(ParseError):
        parse("$read")


@pytest.mark.parametrize("source", [":=", ":= x", ":= 3 x"])
def test_invalid_assign(source: str) -> None:
    with pytest.raises(ParseError):
        parse(source)


@pytest.mark.parametrize(
    "source",
    ["$if", "$if x {}", "$if {} {}", "$if x y {}", "$if x $print x {}"],
)
def test_invalid_if(source: str) -> None:
    with pytest.raises(ParseError):
        parse(source)


@pytest.mark.parametrize(
    "source",
    [
        "$print 3 + x",
        "$print + x",
        "$print - x",
        "$print * x",
        "$print / x",
        "$print < x",
        "$print ~",
        "$print ~ x y",
        "$print + + x y",
        "$print < y",
        "$print < - y z",
    ],
)
def test_invalid_expr(source: str) -> None:
    with pytest.raises(ParseError):
        parse(source)
