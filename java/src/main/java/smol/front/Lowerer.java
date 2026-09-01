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

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import smol.middle.Tir;

/** Lowers the AST to the tiny IR. */
public final class Lowerer {
  private Lowerer() {}

  public static Tir.Program lower(Ast.Program program) {
    return new Lower().lowerProgram(program);
  }

  private sealed interface TvEntry permits Label, Inner, Term {}

  private record Label(String id) implements TvEntry {}

  private record Inner(Tir.Instruction instruction) implements TvEntry {}

  private record Term(Tir.Terminator terminator) implements TvEntry {}

  private static final class Lower {
    private final Set<String> declarations = new TreeSet<>();
    private final List<TvEntry> translationVector = new ArrayList<>();
    private long freshCounter;
    private long blockCounter;

    Tir.Program lowerProgram(Ast.Program program) {
      translationVector.add(new Label("entry"));
      for (var statement : program.stmts()) {
        lowerStmt(statement);
      }
      translationVector.add(new Term(new Tir.Exit()));
      return new Tir.Program(declarations, constructCfg(translationVector));
    }

    private void lowerStmt(Ast.Stmt statement) {
      throw new UnsupportedOperationException("TODO: lower a statement");
    }

    private String lowerExpr(Ast.Expr expression) {
      throw new UnsupportedOperationException("TODO: lower an expression and return its variable");
    }

    private String mkVar(String prefix) {
      throw new UnsupportedOperationException("TODO: create a fresh variable");
    }

    private String mkLabel() {
      throw new UnsupportedOperationException("TODO: create a fresh basic-block label");
    }

    private static java.util.Map<String, Tir.Block> constructCfg(List<TvEntry> entries) {
      throw new UnsupportedOperationException("TODO: construct a CFG from the translation vector");
    }
  }
}
