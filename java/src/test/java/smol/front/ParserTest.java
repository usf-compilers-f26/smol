// Copyright (C) 2026 Mehmet Emre
// SPDX-License-Identifier: GPL-3.0-only
//
// This file is part of smol.
//
// smol is free software: you can redistribute it and/or modify it under the
// terms of the GNU General Public License version 3 as published by the Free
// Software Foundation.
//
// smol is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
// A PARTICULAR PURPOSE. See the GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along with
// smol. If not, see <https://www.gnu.org/licenses/>.

package smol.front;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static smol.front.Ast.BOp.ADD;
import static smol.front.Ast.BOp.DIV;
import static smol.front.Ast.BOp.LT;
import static smol.front.Ast.BOp.MUL;
import static smol.front.Ast.BOp.SUB;

import java.util.List;
import org.junit.jupiter.api.Test;
import smol.front.Ast.Assign;
import smol.front.Ast.BOp;
import smol.front.Ast.BinOp;
import smol.front.Ast.Const;
import smol.front.Ast.Expr;
import smol.front.Ast.If;
import smol.front.Ast.Negate;
import smol.front.Ast.Print;
import smol.front.Ast.Read;
import smol.front.Ast.Var;

final class ParserTest {
  private static Expr bop(BOp op, Expr lhs, Expr rhs) {
    return new BinOp(op, lhs, rhs);
  }

  private static Expr negate(Expr inner) {
    return new Negate(inner);
  }

  private static Expr var(String name) {
    return new Var(name);
  }

  @Test
  void empty() throws ParseException {
    assertEquals(List.of(), Parser.parse("").stmts());
  }

  @Test
  void print() throws ParseException {
    assertEquals(List.of(new Print(new Const(0))), Parser.parse("$print 0").stmts());
  }

  @Test
  void read() throws ParseException {
    assertEquals(List.of(new Read("x")), Parser.parse("$read x").stmts());
  }

  @Test
  void variable() throws ParseException {
    assertEquals(List.of(new Print(var("x"))), Parser.parse("$print x").stmts());
  }

  @Test
  void binaryOperations() throws ParseException {
    assertEquals(List.of(new Print(bop(ADD, var("x"), var("x")))), Parser.parse("$print + x x").stmts());
    assertEquals(List.of(new Print(bop(MUL, var("x"), var("x")))), Parser.parse("$print * x x").stmts());
    assertEquals(List.of(new Print(bop(DIV, var("x"), var("x")))), Parser.parse("$print / x x").stmts());
    assertEquals(List.of(new Print(bop(SUB, var("x"), var("x")))), Parser.parse("$print - x x").stmts());
    assertEquals(List.of(new Print(bop(LT, var("x"), var("x")))), Parser.parse("$print < x x").stmts());
  }

  @Test
  void negation() throws ParseException {
    assertEquals(List.of(new Print(negate(var("x")))), Parser.parse("$print ~ x").stmts());
  }

  @Test
  void complexExpression() throws ParseException {
    assertEquals(
        List.of(new Print(bop(MUL, bop(ADD, var("x"), new Const(3)), bop(DIV, negate(new Const(7)), var("y"))))),
        Parser.parse("$print * + x 3 / ~ 7 y").stmts());
  }

  @Test
  void assignment() throws ParseException {
    assertEquals(List.of(new Assign("x", new Const(3))), Parser.parse(":= x 3").stmts());
    assertEquals(List.of(new Assign("x", bop(ADD, var("x"), new Const(3)))), Parser.parse(":= x + x 3").stmts());
  }

  @Test
  void conditional() throws ParseException {
    assertEquals(List.of(new If(var("x"), List.of(), List.of())), Parser.parse("$if x {} {}").stmts());
    assertEquals(
        List.of(new If(var("x"), List.of(new Print(new Const(0))), List.of(new Assign("x", new Const(3))))),
        Parser.parse("$if x {$print 0} {:= x 3}").stmts());
    assertEquals(
        List.of(new If(var("x"), List.of(new Print(new Const(0)), new Read("x")),
            List.of(new Assign("x", new Const(3)), new Assign("y", var("x"))))),
        Parser.parse("$if x {$print 0 $read x} {:= x 3 := y x}").stmts());
    assertEquals(
        List.of(new If(bop(LT, var("x"), var("y")), List.of(new Print(new Const(0))),
            List.of(new Assign("x", new Const(3))))),
        Parser.parse("$if < x y {$print 0} {:= x 3}").stmts());
  }

  @Test
  void rejectsIllegalProgramStartAndLeftovers() {
    for (var input : List.of("x", "0", "<", ":= x y + z", ":= x y + z t")) {
      assertThrows(ParseException.class, () -> Parser.parse(input));
    }
  }

  @Test
  void rejectsIncompletePrint() {
    assertThrows(ParseException.class, () -> Parser.parse("$print"));
  }

  @Test
  void rejectsIncompleteRead() {
    assertThrows(ParseException.class, () -> Parser.parse("$read"));
  }

  @Test
  void rejectsMalformedAssignment() {
    for (var input : List.of(":=", ":= x", ":= 3 x")) {
      assertThrows(ParseException.class, () -> Parser.parse(input));
    }
  }

  @Test
  void rejectsMalformedConditional() {
    for (var input : List.of("$if", "$if x {}", "$if {} {}", "$if x y {}", "$if x $print x {}")) {
      assertThrows(ParseException.class, () -> Parser.parse(input));
    }
  }

  @Test
  void rejectsMalformedExpression() {
    for (var input : List.of(
        "$print 3 + x", "$print + x", "$print - x", "$print * x", "$print / x",
        "$print < x", "$print ~", "$print ~ x y", "$print + + x y", "$print < y",
        "$print < - y z")) {
      assertThrows(ParseException.class, () -> Parser.parse(input));
    }
  }
}
