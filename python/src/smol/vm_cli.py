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

"""Command-line runner for smol programs on the tiny IR VM."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from smol.front.lower import lower
from smol.front.parse import parse
from smol.vm import run


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="vm", description="Run a smol program")
    parser.add_argument("file", type=Path, help="the smol program file")
    parser.add_argument("inputs", nargs="*", type=int, help="numbers for $read")
    args = parser.parse_args(argv)

    source = args.file.read_text(encoding="utf-8")
    for value in run(lower(parse(source)), args.inputs):
        print(value)


if __name__ == "__main__":
    main()
