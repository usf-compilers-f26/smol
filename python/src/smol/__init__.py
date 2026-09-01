"""The smol teaching compiler."""

from smol.front.lower import lower
from smol.front.parse import ParseError, parse
from smol.middle.opt import optimize

__all__ = ["ParseError", "lower", "optimize", "parse"]
