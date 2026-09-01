import pytest

from smol.front.ast import Assign, BinOp, BOp, Const, If, Negate, Print, Read, Var
from smol.front.parse import ParseError, parse


def test_empty() -> None:
    assert parse("").statements == ()


def test_print() -> None:
    assert parse("$print 0").statements == (Print(Const(0)),)


def test_read() -> None:
    assert parse("$read x").statements == (Read("x"),)


def test_var() -> None:
    assert parse("$print x").statements == (Print(Var("x")),)


@pytest.mark.parametrize(
    ("symbol", "operation"),
    [("+", BOp.ADD), ("*", BOp.MUL), ("/", BOp.DIV), ("-", BOp.SUB), ("<", BOp.LT)],
)
def test_binop(symbol: str, operation: BOp) -> None:
    assert parse(f"$print {symbol} x x").statements == (
        Print(BinOp(operation, Var("x"), Var("x"))),
    )


def test_negate() -> None:
    assert parse("$print ~ x").statements == (Print(Negate(Var("x"))),)


def test_complex_expr() -> None:
    expected = BinOp(
        BOp.MUL,
        BinOp(BOp.ADD, Var("x"), Const(3)),
        BinOp(BOp.DIV, Negate(Const(7)), Var("y")),
    )
    assert parse("$print * + x 3 / ~ 7 y").statements == (Print(expected),)


def test_assign() -> None:
    assert parse(":= x 3").statements == (Assign("x", Const(3)),)
    assert parse(":= x + x 3").statements == (
        Assign("x", BinOp(BOp.ADD, Var("x"), Const(3))),
    )


def test_if() -> None:
    assert parse("$if x {} {}").statements == (If(Var("x"), (), ()),)
    assert parse("$if x {$print 0} {:= x 3}").statements == (
        If(Var("x"), (Print(Const(0)),), (Assign("x", Const(3)),)),
    )
    assert parse("$if x {$print 0 $read x} {:= x 3 := y x}").statements == (
        If(
            Var("x"),
            (Print(Const(0)), Read("x")),
            (Assign("x", Const(3)), Assign("y", Var("x"))),
        ),
    )
    assert parse("$if < x y {$print 0} {:= x 3}").statements == (
        If(
            BinOp(BOp.LT, Var("x"), Var("y")),
            (Print(Const(0)),),
            (Assign("x", Const(3)),),
        ),
    )


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
