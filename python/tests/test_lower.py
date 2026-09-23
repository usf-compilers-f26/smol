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

"""Behavior expected from AST-to-tiny-IR lowering."""

import pytest

from smol.front.lower import lower
from smol.front.parse import parse
from smol.vm import run


@pytest.mark.parametrize(
    ("source", "inputs", "expected"),
    [
        ("", [], []),
        ("$read x := y + x 2 $print y", [40], [42]),
        ("$print never_assigned := later 9 $print later", [], [0, 9]),
        ("$print ~ 7 $print * + 2 3 4", [], [-7, 20]),
        ("$read x $if x {$print 1} {$print 2} $print 3", [0], [2, 3]),
        ("$read x $if x {$print 1} {$print 2} $print 3", [5], [1, 3]),
        (
            "$read x $if < x 0 {$print ~ 1} {$if < 0 x {$print 1} {$print 0}}",
            [-3],
            [-1],
        ),
        (
            "$read x $if < x 0 {$print ~ 1} {$if < 0 x {$print 1} {$print 0}}",
            [0],
            [0],
        ),
        (
            "$read x $if < x 0 {$print ~ 1} {$if < 0 x {$print 1} {$print 0}}",
            [2],
            [1],
        ),
    ],
)
def test_lowered_program_behavior(
    source: str, inputs: list[int], expected: list[int]
) -> None:
    assert run(lower(parse(source)), inputs) == expected
