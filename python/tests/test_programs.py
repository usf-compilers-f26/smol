from pathlib import Path

import pytest

from smol.front.parse import parse

PROGRAMS = Path(__file__).parents[1] / "programs"


@pytest.mark.parametrize(
    "path", sorted(PROGRAMS.glob("*.smol")), ids=lambda path: path.name
)
def test_example_program_parses(path: Path) -> None:
    parse(path.read_text(encoding="utf-8"))
