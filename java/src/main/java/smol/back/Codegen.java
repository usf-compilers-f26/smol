package smol.back;

import smol.middle.Tir;

/** Generates RISC-V assembly from TIR. */
public final class Codegen {
  private Codegen() {}

  public static Asm.Program codeGen(Tir.Program program) {
    throw new UnsupportedOperationException("TODO: generate RISC-V assembly");
  }
}

