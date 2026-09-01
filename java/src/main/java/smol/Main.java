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

package smol;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import smol.back.Codegen;
import smol.front.Lexer;
import smol.front.Lowerer;
import smol.front.ParseException;
import smol.front.Parser;
import smol.middle.Optimizer;
import smol.middle.Tir;

/** Command-line compiler for smol. */
public final class Main {
  private static final String VERSION = "0.1.0";

  private Main() {}

  private enum Output {
    TOKENS,
    AST,
    TIR,
    ASM;

    static Output parse(String value) {
      return switch (value) {
        case "tokens" -> TOKENS;
        case "ast" -> AST;
        case "tir" -> TIR;
        case "asm" -> ASM;
        default -> throw new IllegalArgumentException("unknown output format: " + value);
      };
    }
  }

  private record Arguments(Path file, Output output, boolean optimize) {
    static Arguments parse(String[] args) {
      Path file = null;
      Output output = Output.TOKENS;
      boolean optimize = false;
      for (int i = 0; i < args.length; i++) {
        var arg = args[i];
        if (arg.equals("-O")) {
          optimize = true;
        } else if (arg.equals("-o") || arg.equals("--out")) {
          if (++i == args.length) {
            throw new IllegalArgumentException(arg + " requires a value");
          }
          output = Output.parse(args[i]);
        } else if (arg.startsWith("--out=")) {
          output = Output.parse(arg.substring("--out=".length()));
        } else if (arg.startsWith("-")) {
          throw new IllegalArgumentException("unknown option: " + arg);
        } else if (file == null) {
          file = Path.of(arg);
        } else {
          throw new IllegalArgumentException("only one input file is accepted");
        }
      }
      if (file == null) {
        throw new IllegalArgumentException("usage: smol [-O] [-o tokens|ast|tir|asm] FILE");
      }
      return new Arguments(file, output, optimize);
    }
  }

  private static Tir.Program getIr(String input, boolean optimize) throws ParseException {
    var program = Lowerer.lower(Parser.parse(input));
    return optimize ? Optimizer.optimize(program) : program;
  }

  private static boolean printInformationalOption(String[] args) {
    for (var arg : args) {
      if (arg.equals("-h") || arg.equals("--help")) {
        System.out.println("Usage: smol [OPTIONS] FILE");
        System.out.println();
        System.out.println("Options:");
        System.out.println("  -o, --out <FORMAT>  Output format: tokens, ast, tir, or asm [default: tokens]");
        System.out.println("  -O                   Turn on optimizations");
        System.out.println("  -h, --help           Print help");
        System.out.println("  -V, --version        Print version");
        return true;
      }
      if (arg.equals("-V") || arg.equals("--version")) {
        System.out.println("smol " + VERSION);
        return true;
      }
    }
    return false;
  }

  public static void main(String[] args) throws IOException, ParseException {
    if (printInformationalOption(args)) {
      return;
    }
    var arguments = Arguments.parse(args);
    var input = Files.readString(arguments.file(), StandardCharsets.UTF_8);
    switch (arguments.output()) {
      case TOKENS -> Lexer.getTokens(input).forEach(System.out::println);
      case AST -> System.out.println(Parser.parse(input));
      case TIR -> System.out.println(getIr(input, arguments.optimize()));
      case ASM -> System.out.println(Codegen.codeGen(getIr(input, arguments.optimize())).asmCode());
    }
  }
}
