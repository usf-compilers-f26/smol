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

from pathlib import Path

import pytest

from smol.front.parse import parse

PROGRAMS = Path(__file__).parents[1] / "programs"


@pytest.mark.parametrize(
    "path", sorted(PROGRAMS.glob("*.smol")), ids=lambda path: path.name
)
def test_example_program_parses(path: Path) -> None:
    parse(path.read_text(encoding="utf-8"))
