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

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

final class ProgramCorpusTest {
  private static Stream<Path> programs() {
    return Stream.of(
            "all_ops.smol",
            "arithmetic_edges.smol",
            "assign.smol",
            "implicit_zero.smol",
            "io.smol",
            "lexer_tour.smol",
            "max.smol",
            "polynomial.smol",
            "sign.smol")
        .map(name -> Path.of("programs", name));
  }

  @ParameterizedTest(name = "{0}")
  @MethodSource("programs")
  void parses(Path path) throws IOException, ParseException {
    Parser.parse(Files.readString(path, StandardCharsets.UTF_8));
  }
}
