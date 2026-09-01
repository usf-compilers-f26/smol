import pytest

from smol.back.asm import Program as AssemblyProgram
from smol.back.codegen import code_gen
from smol.front.ast import BOp, Const, Print
from smol.front.ast import Program as AstProgram
from smol.front.lex import Lexer, TokenKind
from smol.front.lower import _Lower, construct_cfg, lower
from smol.front.parse import Parser
from smol.middle.tir import Program as TirProgram


def test_lexer_todos_are_redacted() -> None:
    lexer = Lexer("")
    with pytest.raises(NotImplementedError):
        lexer.end_of_input()
    with pytest.raises(NotImplementedError):
        lexer.skip_whitespace()
    with pytest.raises(NotImplementedError):
        lexer.next()


def test_lowering_is_redacted() -> None:
    with pytest.raises(NotImplementedError):
        lower(AstProgram(()))
    lowerer = _Lower()
    with pytest.raises(NotImplementedError):
        lowerer.lower_stmt(Print(Const(0)))
    with pytest.raises(NotImplementedError):
        lowerer.lower_expr(Const(0))
    with pytest.raises(NotImplementedError):
        lowerer.mk_var("temporary")
    with pytest.raises(NotImplementedError):
        lowerer.mk_label()
    with pytest.raises(NotImplementedError):
        construct_cfg([])


def test_parser_todos_are_redacted() -> None:
    parser = Parser.__new__(Parser)
    parser.tokens = []
    operations = (
        parser.next,
        lambda: parser.next_is(TokenKind.ID),
        lambda: parser.eat(TokenKind.ID),
        lambda: parser.expect(TokenKind.ID),
        parser.parse_program,
        parser.parse_stmt,
        parser.parse_block,
        parser.parse_expr,
        lambda: parser.parse_binop(BOp.ADD),
    )
    for operation in operations:
        with pytest.raises(NotImplementedError):
            operation()


def test_backend_is_redacted() -> None:
    with pytest.raises(NotImplementedError):
        code_gen(TirProgram(frozenset(), {}))
    program = AssemblyProgram("main", {}, 0, ())
    with pytest.raises(NotImplementedError):
        program.asm_code()
