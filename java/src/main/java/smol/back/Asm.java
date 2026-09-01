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

package smol.back;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;

/** The 64-bit RISC-V (RV64G) assembly model. */
public final class Asm {
  public static final int WORD_SIZE = 8;
  public static final int LOG2_WORD_SIZE = 3;
  public static final String GC_INIT_FUNCTION = "_cflat_init_gc";
  public static final String ALLOC_FUNCTION = "_cflat_alloc";

  private Asm() {}

  public enum Register {
    ZERO("zero"), RA("ra"), SP("sp"), GP("gp"), TP("tp"), T0("t0"), T1("t1"), T2("t2"),
    FP("fp"), S1("s1"), A0("a0"), A1("a1"), A2("a2"), A3("a3"), A4("a4"), A5("a5"),
    A6("a6"), A7("a7"), S2("s2"), S3("s3"), S4("s4"), S5("s5"), S6("s6"), S7("s7"),
    S8("s8"), S9("s9"), S10("s10"), S11("s11"), T3("t3"), T4("t4"), T5("t5"), T6("t6");

    private final String text;

    Register(String text) {
      this.text = text;
    }

    @Override
    public String toString() {
      return text;
    }
  }

  public static final List<Register> ARGUMENT_REGISTERS =
      List.of(
          Register.A0,
          Register.A1,
          Register.A2,
          Register.A3,
          Register.A4,
          Register.A5,
          Register.A6,
          Register.A7);

  public sealed interface Memory permits Mem, Global {
    Memory offset(int amount);

    Optional<Register> usedRegister();
  }

  public record Mem(Register register, int displacement) implements Memory {
    @Override
    public Memory offset(int amount) {
      return new Mem(register, displacement + amount);
    }

    @Override
    public Optional<Register> usedRegister() {
      return Optional.of(register);
    }

    @Override
    public String toString() {
      return displacement + "(" + register + ")";
    }
  }

  public record Global(int index, int displacement) implements Memory {
    @Override
    public Memory offset(int amount) {
      return new Global(index, displacement + amount);
    }

    @Override
    public Optional<Register> usedRegister() {
      return Optional.empty();
    }

    @Override
    public String toString() {
      return displacement + "(global#" + index + ")";
    }
  }

  /** A register or memory location accessible to an instruction. */
  public sealed interface Location permits MemoryLocation, RegisterLocation {
    Optional<Register> usedRegister();

    Optional<Memory> memory();

    Location offset(int amount);
  }

  public record MemoryLocation(Memory value) implements Location {
    @Override
    public Optional<Register> usedRegister() {
      return value.usedRegister();
    }

    @Override
    public Optional<Memory> memory() {
      return Optional.of(value);
    }

    @Override
    public Location offset(int amount) {
      return new MemoryLocation(value.offset(amount));
    }
  }

  public record RegisterLocation(Register value) implements Location {
    @Override
    public Optional<Register> usedRegister() {
      return Optional.of(value);
    }

    @Override
    public Optional<Memory> memory() {
      return Optional.empty();
    }

    @Override
    public Location offset(int amount) {
      if (amount != 0) {
        throw new IllegalStateException("cannot take a non-zero offset from a register");
      }
      return this;
    }
  }

  public enum Condition {
    EQUAL("eq"), NOT_EQUAL("ne"), LESS("lt"), LESS_EQUAL("le"), GREATER("gt"), GREATER_EQUAL("ge");

    private final String text;

    Condition(String text) {
      this.text = text;
    }

    @Override
    public String toString() {
      return text;
    }
  }

  public enum ArithOp {
    ADD("add"), SUB("sub"), MUL("mul"), DIV("div"), SLT("slt"), AND("and"), OR("or"),
    XOR("xor"), SRL("srl"), SRA("sra"), SLL("sll");

    private final String text;

    ArithOp(String text) {
      this.text = text;
    }

    @Override
    public String toString() {
      return text;
    }
  }

  public sealed interface JumpTarget permits Local, GlobalTarget {}

  public record Local(String id) implements JumpTarget {}

  public record GlobalTarget(String id) implements JumpTarget {}

  private static String targetText(JumpTarget target) {
    return switch (target) {
      case Local(var id) -> id + " # local, basic block";
      case GlobalTarget(var id) -> id + " # global, function";
    };
  }

  public sealed interface Instruction
      permits La, Ld, Sd, Li, Arith, ArithI, Jal, Jalr, Branch, CompareZero, Comment {
    default List<Register> usedRegisters() {
      return switch (this) {
        case La(var dst, var src) ->
            src.usedRegister().map(register -> List.of(dst, register)).orElseGet(() -> List.of(dst));
        case Ld(var dst, var src) ->
            src.usedRegister().map(register -> List.of(dst, register)).orElseGet(() -> List.of(dst));
        case Sd(var dst, var src) ->
            dst.usedRegister().map(register -> List.of(register, src)).orElseGet(() -> List.of(src));
        case Li(var dst, _) -> List.of(dst);
        case Arith(_, var dst, var lhs, var rhs) -> List.of(dst, lhs, rhs);
        case ArithI(_, var dst, var lhs, _) -> List.of(dst, lhs);
        case Jal(var dst, _) -> List.of(dst);
        case Jalr(var dst, var target) -> List.of(target, dst);
        case Branch(_, var lhs, var rhs, _) -> List.of(lhs, rhs);
        case CompareZero(var dst, var lhs, _) -> List.of(lhs, dst);
        case Comment(_) -> List.of();
      };
    }

    static Instruction jump(JumpTarget target) {
      return new Jal(Register.ZERO, target);
    }

    static Instruction call(String callee) {
      return new Jal(Register.RA, new GlobalTarget(callee));
    }

    static Instruction move(Register dst, Register src) {
      return new ArithI(ArithOp.ADD, dst, src, 0);
    }

    static Instruction read(Register dst, Location src) {
      return switch (src) {
        case RegisterLocation(var register) -> move(dst, register);
        case MemoryLocation(var memory) -> new Ld(dst, memory);
      };
    }

    static Instruction write(Location dst, Register src) {
      return switch (dst) {
        case RegisterLocation(var register) -> move(register, src);
        case MemoryLocation(var memory) -> new Sd(memory, src);
      };
    }
  }

  public record La(Register dst, Memory src) implements Instruction {
    @Override
    public String toString() {
      return "la " + dst + ", " + src;
    }
  }

  public record Ld(Register dst, Memory src) implements Instruction {
    @Override
    public String toString() {
      return "ld " + dst + ", " + src;
    }
  }

  public record Sd(Memory dst, Register src) implements Instruction {
    @Override
    public String toString() {
      return "sd " + src + ", " + dst;
    }
  }

  public record Li(Register dst, long immediate) implements Instruction {
    @Override
    public String toString() {
      return "li " + dst + ", " + immediate;
    }
  }

  public record Arith(ArithOp op, Register dst, Register lhs, Register rhs) implements Instruction {
    @Override
    public String toString() {
      return op + " " + dst + ", " + lhs + ", " + rhs;
    }
  }

  public record ArithI(ArithOp op, Register dst, Register lhs, int rhs) implements Instruction {
    @Override
    public String toString() {
      return op + "i " + dst + ", " + lhs + ", " + rhs;
    }
  }

  public record Jal(Register dst, JumpTarget target) implements Instruction {
    @Override
    public String toString() {
      return "jal " + dst + ", " + targetText(target);
    }
  }

  public record Jalr(Register dst, Register target) implements Instruction {
    @Override
    public String toString() {
      return "jalr " + dst + ", " + target;
    }
  }

  public record Branch(Condition condition, Register lhs, Register rhs, JumpTarget target)
      implements Instruction {
    @Override
    public String toString() {
      return "b" + condition + " " + lhs + ", " + rhs + ", " + targetText(target);
    }
  }

  public record CompareZero(Register dst, Register lhs, Condition condition) implements Instruction {
    @Override
    public String toString() {
      return "s" + condition + "z " + dst + ", " + lhs;
    }
  }

  public record Comment(String text) implements Instruction {
    @Override
    public String toString() {
      return "# \"" + text.replace("\"", "\\\"") + "\"";
    }
  }

  public record BasicBlock(String id, List<Instruction> instructions) {
    public BasicBlock {
      instructions = List.copyOf(instructions);
    }
  }

  public record Program(
      String id, Map<String, BasicBlock> basicBlocks, int stackSpace, List<Register> usedRegisters) {
    public Program {
      basicBlocks = Collections.unmodifiableMap(new TreeMap<>(basicBlocks));
      usedRegisters = List.copyOf(usedRegisters);
    }

    public String asmCode() {
      throw new UnsupportedOperationException("TODO: generate the final assembly code");
    }
  }
}
