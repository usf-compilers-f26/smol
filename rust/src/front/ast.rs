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

//! The abstract syntax tree.

use derive_more::derive::Display;

use crate::common::Id;

#[derive(Debug)]
pub struct Program {
    pub stmts: Vec<Stmt>,
}

#[derive(Debug, PartialEq, Eq)]
pub enum Stmt {
    Assign(Id, Expr),
    Print(Expr),
    Read(Id),
    If {
        guard: Expr,
        tt: Vec<Stmt>,
        ff: Vec<Stmt>,
    },
}

#[derive(Debug, PartialEq, Eq)]
pub enum Expr {
    Var(Id),
    Const(i64),
    BinOp {
        op: BOp,
        lhs: Box<Expr>,
        rhs: Box<Expr>,
    },
    Negate(Box<Expr>),
}

#[derive(Debug, PartialEq, Eq, Clone, Copy, Display)]
pub enum BOp {
    #[display("mul")]
    Mul,
    #[display("div")]
    Div,
    #[display("add")]
    Add,
    #[display("sub")]
    Sub,
    #[display("lt")]
    Lt,
}
