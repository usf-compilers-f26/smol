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

use super::*;

pub(super) fn construct_cfg(tv: Vec<TvEntry>) -> Map<Id, Block> {
    let mut entry_p = tv.into_iter().peekable();
    let mut blocks = Map::new();

    while let Some(Label(bb_id)) = entry_p.peek().cloned() {
        entry_p.next();
        let mut insn = vec![];
        while let Some(Inner(i)) = entry_p.peek() {
            insn.push(i.clone());
            entry_p.next();
        }
        let Some(Term(term)) = entry_p.next() else {
            panic!("Malformed translation vector: the basic block {bb_id:?} does not end with a terminator");
        };

        if blocks.insert(bb_id, Block { insn, term }).is_some() {
            panic!("Malformed translation vector: the basic block {bb_id:?} is defined multiple times");
        }
    }

    if let Some(entry) = entry_p.next() {
        panic!("The translation vector is not well-formed, found a non-label at the beginning of a basic block: {entry:?}");
    }

    blocks
}
