package smol.front;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import org.junit.jupiter.api.Test;
import smol.front.Lexer.Token;
import smol.front.Lexer.TokenKind;

final class LexerTest {
  private static Token id(String text) {
    return new Token(TokenKind.ID, text);
  }

  private static Token num(String text) {
    return new Token(TokenKind.NUM, text);
  }

  private static Token error(String text) {
    return new Token(TokenKind.ERROR, text);
  }

  private static Token token(TokenKind kind) {
    return new Token(kind, kind.toString());
  }

  @Test
  void skipWhitespace() {
    var lexer = new Lexer("foo");
    lexer.skipWhitespace();
    assertEquals(0, lexer.position());
    lexer = new Lexer(" \n\t  foo");
    lexer.skipWhitespace();
    assertEquals(5, lexer.position());
    lexer = new Lexer(" // stuff\n\t  foo ");
    lexer.skipWhitespace();
    assertEquals(13, lexer.position());
  }

  @Test
  void empty() {
    assertEquals(List.of(), Lexer.getTokens(""));
    assertEquals(List.of(), Lexer.getTokens("  \n//hello\n"));
    assertEquals(List.of(), Lexer.getTokens("  \n//hi"));
  }

  @Test
  void singleToken() {
    assertEquals(List.of(id("x")), Lexer.getTokens("x"));
    assertEquals(List.of(id("print")), Lexer.getTokens("print"));
    assertEquals(List.of(id("if")), Lexer.getTokens("if"));
    assertEquals(List.of(id("yolo")), Lexer.getTokens("yolo"));
    assertEquals(List.of(num("3")), Lexer.getTokens("3"));
    assertEquals(List.of(num("0345678910")), Lexer.getTokens("0345678910"));
    assertEquals(List.of(error("%")), Lexer.getTokens("%"));
    for (var kind :
        List.of(
            TokenKind.ASSIGN,
            TokenKind.PRINT,
            TokenKind.READ,
            TokenKind.IF,
            TokenKind.LBRACE,
            TokenKind.RBRACE,
            TokenKind.PLUS,
            TokenKind.MINUS,
            TokenKind.MUL,
            TokenKind.DIV,
            TokenKind.LT,
            TokenKind.TILDE)) {
      assertEquals(List.of(token(kind)), Lexer.getTokens(kind.toString()));
    }
  }

  @Test
  void multiToken() {
    assertEquals(
        List.of(
            id("x"), token(TokenKind.PRINT), token(TokenKind.READ), token(TokenKind.IF),
            token(TokenKind.LBRACE), token(TokenKind.RBRACE), token(TokenKind.PLUS), num("0"),
            token(TokenKind.MINUS), token(TokenKind.MUL), error("$"), token(TokenKind.DIV),
            token(TokenKind.LT)),
        Lexer.getTokens("x$print$read$if{}+0-*$/<"));
    assertEquals(
        List.of(
            id("x"), id("yz"), token(TokenKind.PRINT), token(TokenKind.READ), token(TokenKind.IF),
            token(TokenKind.LBRACE), token(TokenKind.RBRACE), token(TokenKind.PLUS), num("0"),
            token(TokenKind.MINUS), token(TokenKind.MUL), error("$"), id("read"),
            token(TokenKind.DIV), token(TokenKind.LT), token(TokenKind.TILDE)),
        Lexer.getTokens("x yz $print $read $if { } +  0   -  //hi\n * $ read / < ~"));
  }
}

