from pathlib import Path

from smol.cli import _argument_parser


def test_tokens_are_default_output() -> None:
    args = _argument_parser().parse_args([str(Path("input.smol"))])
    assert args.out == "tokens"
    assert args.optimize is False
