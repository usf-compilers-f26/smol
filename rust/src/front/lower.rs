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

//! Lowering

mod hidden;
use hidden::*;
use super::ast;
use super::BOp;
use ast::Stmt;
use ast::Expr;
use crate::{
    common::{id, Id},
    middle::tir,
};
use std::collections::{BTreeMap as Map, BTreeSet as Set};
use tir::{Block, Instruction, Terminator};
use TvEntry::*;

pub fn lower(program: ast::Program) -> tir::Program {
    let lower = Lower::new();
    lower.lower_program(program)
}

// Entries in the translation vector
#[derive(Debug, Clone)]
enum TvEntry {
    // A basic block label
    Label(Id),
    // An inner (non-terminating) instruction
    Inner(Instruction),
    // A terminal instruction
    Term(Terminator),
}

impl TvEntry {
    fn get_inner(self) -> Option<Instruction> {
        if let Inner(i) = self {
            Some(i)
        } else {
            None
        }
    }
}

// Lowering data
struct Lower {
    decl: Set<Id>,
    // translation vector
    tv: Vec<TvEntry>,
    // for creating fresh locals
    fresh_ctr: i64,
    // for creating fresh block labels
    bb_ctr: i64,
}

impl Lower {
    fn new() -> Self {
        Lower {
            decl: Set::new(),
            tv: vec![],
            fresh_ctr: 0,
            bb_ctr: 0,
        }
    }

    // add given variable to declared variables
    fn add_decl(&mut self, var: Id) {
        self.decl.insert(var);
    }

    fn lower_program(mut self, program: ast::Program) -> tir::Program {
        self.tv.push(Label(id("entry")));

        for stmt in program.stmts {
            self.lower_stmt(stmt);
        }
        // Close the last basic block
        self.tv.push(Term(Terminator::Exit));

        tir::Program {
            decl: self.decl,
            block: construct_cfg(self.tv),
        }
    }

    fn lower_stmt(&mut self, stmt: Stmt) {
        todo!()
    }

    fn lower_expr(&mut self, e: Expr) -> Id {
        todo!("return the variable holding the value")
    }

    fn mk_var(&mut self, prefix: &str) -> Id {
        todo!("return the variable name")
    }

    fn mk_label(&mut self) -> Id {
        todo!("create and return a fresh label")
    }
}
