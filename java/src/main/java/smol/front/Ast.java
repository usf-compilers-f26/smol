package smol.front;

import java.util.List;

/** The abstract syntax tree. */
public final class Ast {
  private Ast() {}

  public record Program(List<Stmt> stmts) {
    public Program {
      stmts = List.copyOf(stmts);
    }
  }

  public sealed interface Stmt permits Assign, Print, Read, If {}

  public record Assign(String id, Expr expr) implements Stmt {}

  public record Print(Expr expr) implements Stmt {}

  public record Read(String id) implements Stmt {}

  public record If(Expr guard, List<Stmt> tt, List<Stmt> ff) implements Stmt {
    public If {
      tt = List.copyOf(tt);
      ff = List.copyOf(ff);
    }
  }

  public sealed interface Expr permits Var, Const, BinOp, Negate {}

  public record Var(String id) implements Expr {}

  public record Const(long value) implements Expr {}

  public record BinOp(BOp op, Expr lhs, Expr rhs) implements Expr {}

  public record Negate(Expr inner) implements Expr {}

  public enum BOp {
    MUL("mul"),
    DIV("div"),
    ADD("add"),
    SUB("sub"),
    LT("lt");

    private final String text;

    BOp(String text) {
      this.text = text;
    }

    @Override
    public String toString() {
      return text;
    }
  }
}

