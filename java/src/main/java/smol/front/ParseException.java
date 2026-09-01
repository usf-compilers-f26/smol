package smol.front;

/** A syntax error in smol source code. */
public final class ParseException extends Exception {
  private static final long serialVersionUID = 1L;

  public ParseException(String message) {
    super("Parse error: " + message);
  }
}

