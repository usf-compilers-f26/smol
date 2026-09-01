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

package smol.middle;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import smol.front.Ast.BOp;

/** The tiny intermediate representation. */
public final class Tir {
  private Tir() {}

  public record Program(Set<String> declarations, Map<String, Block> blocks) {
    public Program {
      declarations = Collections.unmodifiableSet(new TreeSet<>(declarations));
      blocks = Collections.unmodifiableMap(new TreeMap<>(blocks));
    }

    @Override
    public String toString() {
      var result = new StringBuilder("let ");
      for (var declaration : declarations) {
        result.append(declaration).append(", ");
      }
      result.append(System.lineSeparator());
      for (var entry : blocks.entrySet()) {
        result.append(entry.getKey()).append(':').append(System.lineSeparator());
        for (var instruction : entry.getValue().instructions()) {
          result.append("    ").append(instruction).append(System.lineSeparator());
        }
        result.append("    ").append(entry.getValue().terminator()).append(System.lineSeparator());
      }
      return result.toString();
    }
  }

  public record Block(List<Instruction> instructions, Terminator terminator) {
    public Block {
      instructions = List.copyOf(instructions);
    }
  }

  public sealed interface Instruction permits Copy, Const, Arith, Read, Print {}

  public record Copy(String dst, String src) implements Instruction {
    @Override
    public String toString() {
      return dst + " = $copy " + src;
    }
  }

  public record Const(String dst, long src) implements Instruction {
    @Override
    public String toString() {
      return dst + " = $const " + src;
    }
  }

  public record Arith(BOp op, String dst, String lhs, String rhs) implements Instruction {
    @Override
    public String toString() {
      return dst + " = $arith " + op + " " + lhs + " " + rhs;
    }
  }

  public record Read(String id) implements Instruction {
    @Override
    public String toString() {
      return "$read " + id;
    }
  }

  public record Print(String id) implements Instruction {
    @Override
    public String toString() {
      return "$print " + id;
    }
  }

  public sealed interface Terminator permits Exit, Jump, Branch {}

  public record Exit() implements Terminator {
    @Override
    public String toString() {
      return "$exit";
    }
  }

  public record Jump(String label) implements Terminator {
    @Override
    public String toString() {
      return "$jump " + label;
    }
  }

  public record Branch(String guard, String tt, String ff) implements Terminator {
    @Override
    public String toString() {
      return "$branch " + guard + " " + tt + " " + ff;
    }
  }

  /** Returns a mutable instruction list convenient for compiler construction. */
  public static List<Instruction> instructions() {
    return new ArrayList<>();
  }
}
