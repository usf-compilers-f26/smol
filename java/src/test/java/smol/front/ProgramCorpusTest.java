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
