package smol.front;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import smol.front.Ast.BOp;
import smol.front.Ast.Expr;
import smol.front.Ast.Program;
import smol.front.Ast.Stmt;
import smol.front.Lexer.Token;
import smol.front.Lexer.TokenKind;

/** Recursive-descent parser for smol. */
public final class Parser {
  private final List<Token> tokens;

  public Parser(String input) {
    tokens = new ArrayList<>(Lexer.getTokens(input));
    Collections.reverse(tokens);
  }

  public static Program parse(String input) throws ParseException {
    var parser = new Parser(input);
    var program = parser.parseProgram();
    if (!parser.tokens.isEmpty()) {
      throw new ParseException("There are still leftover tokens after reading a whole program.");
    }
    return program;
  }

  Optional<Token> peek() {
    return tokens.isEmpty() ? Optional.empty() : Optional.of(tokens.getLast());
  }

  Token next() throws ParseException {
    throw new UnsupportedOperationException("TODO: consume the next token");
  }

  boolean nextIs(TokenKind kind) {
    throw new UnsupportedOperationException("TODO: inspect the next token kind");
  }

  boolean eat(TokenKind kind) {
    throw new UnsupportedOperationException("TODO: optionally consume a token");
  }

  Token expect(TokenKind kind) throws ParseException {
    throw new UnsupportedOperationException("TODO: consume an expected token");
  }

  Program parseProgram() throws ParseException {
    throw new UnsupportedOperationException("TODO: parse a program");
  }

  Stmt parseStmt() throws ParseException {
    throw new UnsupportedOperationException("TODO: parse a statement");
  }

  List<Stmt> parseBlock() throws ParseException {
    throw new UnsupportedOperationException("TODO: parse a block");
  }

  Expr parseExpr() throws ParseException {
    throw new UnsupportedOperationException("TODO: parse an expression");
  }

  Expr parseBinOp(BOp op) throws ParseException {
    throw new UnsupportedOperationException("TODO: parse both binary operands");
  }
}
