package smol.front;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.regex.Pattern;

/** Regex-based lexer for smol source code. */
public final class Lexer {
  public enum TokenKind {
    ID("id"),
    NUM("num"),
    ASSIGN(":="),
    PRINT("$print"),
    READ("$read"),
    IF("$if"),
    LBRACE("{"),
    RBRACE("}"),
    PLUS("+"),
    MINUS("-"),
    MUL("*"),
    DIV("/"),
    LT("<"),
    TILDE("~"),
    ERROR("error");

    private final String text;

    TokenKind(String text) {
      this.text = text;
    }

    @Override
    public String toString() {
      return text;
    }
  }

  public record Token(TokenKind kind, String text) {
    @Override
    public String toString() {
      return "kind: '" + kind + "', part of input: '" + text + "'";
    }
  }

  private record Recognizer(Pattern pattern, TokenKind kind) {}

  private static final Pattern WHITESPACE = Pattern.compile("(?:[ \\t\\f\\r\\n\\u000B]|(?://.*))*");
  private static final List<Recognizer> RECOGNIZERS =
      List.of(
          recognizer("\\$print", TokenKind.PRINT),
          recognizer("\\$read", TokenKind.READ),
          recognizer("\\$if", TokenKind.IF),
          recognizer("\\{", TokenKind.LBRACE),
          recognizer("}", TokenKind.RBRACE),
          recognizer(":=", TokenKind.ASSIGN),
          recognizer("\\+", TokenKind.PLUS),
          recognizer("-", TokenKind.MINUS),
          recognizer("\\*", TokenKind.MUL),
          recognizer("/", TokenKind.DIV),
          recognizer("<", TokenKind.LT),
          recognizer("[a-zA-Z_][a-zA-Z0-9_]*", TokenKind.ID),
          recognizer("[0-9]+", TokenKind.NUM),
          recognizer("~", TokenKind.TILDE));

  private final String input;
  private int position;

  public Lexer(String input) {
    this.input = input;
  }

  private static Recognizer recognizer(String regex, TokenKind kind) {
    return new Recognizer(Pattern.compile(regex), kind);
  }

  /** Returns whether all input has been consumed. */
  public boolean endOfInput() {
    throw new UnsupportedOperationException("TODO: detect the end of input");
  }

  /** Skips comments and whitespace. */
  void skipWhitespace() {
    throw new UnsupportedOperationException("TODO: skip comments and whitespace");
  }

  /** Returns the next token, or an empty optional at end of input. */
  public Optional<Token> next() {
    throw new UnsupportedOperationException("TODO: produce the next token");
  }

  int position() {
    return position;
  }

  /** Reads every token from the input. */
  public static List<Token> getTokens(String input) {
    var lexer = new Lexer(input);
    var tokens = new ArrayList<Token>();
    while (true) {
      var token = lexer.next();
      if (token.isEmpty()) {
        break;
      }
      tokens.add(token.orElseThrow());
    }
    return List.copyOf(tokens);
  }
}
