//! The 64-bit RISCV (RV64G) backend.
//!
//! The backend fuses the register allocation into code generation (there is no
//! separate register allocator), which is simpler than the full CFlat compiler.
//!
//! Additionally, we have a much simpler program structure (we need to call only
//! runtime functions, and there are no function definitions).  So, an output
//! program is just a sequence of instructions and labels.
//!
//! # Design decisions
//!
//! We use RV64G ABI (called *risc-v* or *riscv* henceforth), so the rest of the
//! documentation focuses on what this ABI looks like.  This ABI is used by
//! Linux on contemporary 64-bit RISC-V CPUs, and by the RISC-V proxy kernel.
//!
//! See <https://riscv.org/wp-content/uploads/2015/01/riscv-calling.pdf> for the
//! ABI specification.
//!
//! Our treatment of the ABI is simpler because of the following design decisions:
//! - All our primitives are 64 bits so we don't need to deal with words < 8 bytes.
//! - We never put aggregates on the stack (or pass them between functions) so we
//!   don't need to handle large return values.
//!
//! # Call stack frame
//!
//! In risc-v, the stack grows down (from higher memory addresses to lower memory
//! addresses).  Also, the stack is always 2-word-aligned.  This means that each
//! stack frame begins at a 128-bit (16-Byte) aligned memory location.
//!
//! Here is a single function's frame, we see how it interacts with the function
//! that called it (the caller):
//!
//! ```txt
//!
//!   High memory addresses
//!
//!   +-------------------------+
//!   | Previous stack frame    |
//!   | (belongs to the caller) |
//!   |       ...               |
//!   +-------------------------+
//!   | Caller-saved registers  |
//!   +-------------------------+
//!   | Argument data           |
//!   +-------------------------+
//!   | Return address          |
//!   +-------------------------+
//!   | Saved frame pointer     | <- Current Frame Pointer (fp)
//!   +-------------------------+
//!   | Local variables         |
//!   +-------------------------+
//!   | Callee-saved registers  |
//!   +-------------------------+ <- Stack Pointer (sp)
//!
//!   Low memory addresses
//! ```
//!
//! - The current stack frame is between what fp and sp point to.
//!
//! - The caller saves registers designated as caller-saved, and puts some of
//!   the arguments on the stack before making the call (see the calling
//!   convention below).
//!
//! - *NOTE:* `fp` and `s0` correspond to the same physical register, so our
//!   compiler never uses s0 to simplify reasoning about register allocation.
//!
//! # Calling convention
//!
//! The calling convention here is a simplified version of the full calling
//! convention.  Specifically, we do not handle passing floating point values.
//!
//! 1. The caller saves caller-saved registers (by pushing them to the stack).
//! 2. The caller places the argument values to the registers and the stack (see
//!    argument handling below).
//! 3. The caller also saves the return address to the stack, and adjusts the
//!    stack pointer.
//!    - At this point, the stack pointer points to the return address.
//! 3. The caller executes the `jal` or `jalr` instruction, which saves the
//!    return address to the given register and jumps to the callee.
//! 4. The callee creates a new stack frame
//!    - This is done by saving the caller's frame pointer, then moving the
//!      stack pointer to the frame pointer.
//!    - After this point, the frame pointer should point to the saved frame
//!      pointer.
//! 5. The callee reserves the stack space for locals & saved registers.
//! 6. The callee saves callee-saved registers (except the frame pointer and the
//!    stack pointer).
//!    - This is done by the register allocator.
//! 7. The callee code is executed, then callee puts the return value to a0 (or
//!    a1:a0, see below).
//! 8. The callee restores callee-saved registers (first general-purpose
//!    registers, then the frame pointer and the stack pointer).
//!    - This is done by the register allocator.
//! 9. The callee jumps back to the caller by jumping to the saved return
//!    address.
//! 10. The caller frees the space allocated for arguments (this is done by
//!     updating the stack pointer).
//! 11. The caller restores caller-saved registers.
//! 12. The caller puts the return value to the lhs of the call instruction.
//!
//! ## Argument-passing
//!
//! We deal with passing at most 1 argument and always returning 1 argument
//! (`print` doesn't need to return anything but we can pretend that it does).
//! The passed argument and the return value are both stored on a0.
//!
//! # Registers
//!
//! ## Caller-saved registers
//!
//! These registers need to be saved by the caller before executing the `call`
//! instruction (if they are used by the caller).
//!
//! - ra (return address), t0--t7 (temporary registers), a0--a7 (argument
//!   registers).
//!
//! ## Callee-saved registers
//!
//! These registers need to be saved by the callee at function entry if they are
//! used by the callee.
//!
//! - fp (a.k.a. s0) and sp are the frame pointer and the stack pointer
//!   respectively.
//! - s1--s11 are general-purpose callee-saved registers.
//!
//! ## Reservation of temporary registers
//!
//! - the code generator is permitted to use t0--t6 as long as their use don't
//!   span multiple instructions.
//!
//! # Register allocation
//!
//! There is no register allocator, all variables are saved on the stack.
#![allow(dead_code)]

use derive_more::Display;
use std::collections::BTreeMap as Map;

use crate::common::*;

use Location::*;
use Memory::*;
use Register::*;

/// Word and pointer size for this processor
const WORD_SIZE: i32 = 8;
const LOG2_WORD_SIZE: i32 = 3;

/// The name of the GC initializer
const GC_INIT_FN: &str = "_cflat_init_gc";

/// The name of the allocation function provided by the runtime
const ALLOC_FN: &str = "_cflat_alloc";

// Argument registers used in the RISC-V ABI
static ARG_REGISTERS: [Register; 8] = [A0, A1, A2, A3, A4, A5, A6, A7];

/// Registers for the actual risc-v machine, in the order in the register file.
#[derive(Clone, Copy, Debug, Display, Eq, Hash, PartialEq, PartialOrd, Ord)]
#[allow(missing_docs)]
pub enum Register {
    #[display("zero")]
    Zero,
    #[display("ra")]
    Ra,
    #[display("sp")]
    Sp,
    #[display("gp")]
    Gp,
    #[display("tp")]
    Tp,
    #[display("t0")]
    T0,
    #[display("t1")]
    T1,
    #[display("t2")]
    T2,
    #[display("fp")]
    Fp,
    #[display("s1")]
    S1,
    #[display("a0")]
    A0,
    #[display("a1")]
    A1,
    #[display("a2")]
    A2,
    #[display("a3")]
    A3,
    #[display("a4")]
    A4,
    #[display("a5")]
    A5,
    #[display("a6")]
    A6,
    #[display("a7")]
    A7,
    #[display("s2")]
    S2,
    #[display("s3")]
    S3,
    #[display("s4")]
    S4,
    #[display("s5")]
    S5,
    #[display("s6")]
    S6,
    #[display("s7")]
    S7,
    #[display("s8")]
    S8,
    #[display("s9")]
    S9,
    #[display("s10")]
    S10,
    #[display("s11")]
    S11,
    #[display("t3")]
    T3,
    #[display("t4")]
    T4,
    #[display("t5")]
    T5,
    #[display("t6")]
    T6,
}

/// Memory locations that RISC-V instructions can access to.
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug, Display)]
enum Memory {
    /// A memory location whose value is in the given register + offset
    #[display("{}({})", _1, _0)]
    Mem(Register, i32),
    /// A global variable with offset.  Effectively, this address is calculated
    /// via an offset from the PC, but we represent it as if it is an absolute
    /// value we can store to keep the backend simple until final assembly-out
    /// step.
    #[display("{}(global#{})", offset, index)]
    Global {
        /// This is an index into the vector globals in [Program].  Using an
        /// index here allows deriving the [Copy] trait.
        index: usize,
        offset: i32,
    },
}

impl Memory {
    /// Return registers that are used to describe this location.
    pub fn used_registers(&self) -> Option<Register> {
        match self {
            Mem(r, _offset) => Some(*r),
            Global { .. } => None,
        }
    }

    /// Get a memory location with given offset from this location.
    pub fn offset(&self, offset: i32) -> Memory {
        match *self {
            Mem(r, off) => Mem(r, off + offset),
            Global { index, offset: off } => Global {
                index,
                offset: off + offset,
            },
        }
    }
}
/// Locations (both memory and register) that RISC-V instructions can access to.
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug)]
enum Location {
    /// A memory location
    MemoryL(Memory),
    Reg(Register),
}

impl Location {
    /// Return registers that are used to describe this location.
    pub fn used_registers(&self) -> Option<Register> {
        match self {
            MemoryL(m) => m.used_registers(),
            Reg(r) => Some(*r),
        }
    }

    pub fn get_memory(&self) -> Option<&Memory> {
        match self {
            MemoryL(m) => Some(m),
            Reg(_) => None,
        }
    }

    /// Get a memory location with given offset from this location.
    pub fn offset(&self, offset: i32) -> Location {
        match self {
            Reg(_) if offset == 0 => *self,
            Reg(_) => {
                unimplemented!("internal error: tried to take non-zero offset from a register")
            }
            MemoryL(m) => MemoryL(m.offset(offset)),
        }
    }
}

// TODO: talk about pseudo instructions

/// A RISC-V instruction that is parametric over the register type.
#[derive(Clone, Eq, PartialEq, Debug)]
enum Instruction {
    La {
        dst: Register,
        src: Memory,
    },
    Ld {
        dst: Register,
        src: Memory,
    },
    Sd {
        dst: Memory,
        src: Register,
    },
    Li {
        dst: Register,
        imm: i64,
    },
    /// Basic arithmetic operations between two registers: addition,
    /// subtraction, multiplication, division, and bit operations.  See
    /// [ArithOp] for supported operations.
    Arith {
        op: ArithOp,
        dst: Register,
        lhs: Register,
        rhs: Register,
    },
    /// Basic arithmetic operations between a register and an immediate:
    /// addition, subtraction, multiplication, division, and bit operations.
    /// See [ArithOp] for supported operations.
    ///
    /// These instructions are decomposed to `li` followed by r-type arithmetic
    /// instructions later.
    ArithI {
        op: ArithOp,
        dst: Register,
        lhs: Register,
        rhs: i32,
    },
    /// Jump to a label (a fixed memory address).  This emits just a `jal`
    /// instruction that stores the instruction pointer and jumps to the target.
    /// The rest of the program is responsible for implementing the correct
    /// function call protocol when using this instruction for calls.
    Jal {
        dst: Register,
        target: JumpTarget,
    }, // can also be used for jumps
    /// Jump to an address stored in a memory location.  This emits just a
    /// `jalr` instruction that stores the instruction pointer and jumps to the
    /// target.  The rest of the program is responsible for implementing the
    /// correct function call protocol when using this instruction for calls and
    /// returns.
    Jalr {
        dst: Register,
        target: Register,
    },
    Branch {
        cond: Condition,
        lhs: Register,
        rhs: Register,
        target: JumpTarget,
    },
    /// Pseudo-ops seqz, snez, sltz, sgtz, ... :
    /// dst = 1 if lhs cond 0, otherwise dst = 0.
    SCmpZ {
        dst: Register,
        lhs: Register,
        cond: Condition,
    },
    /// In-line comments in the output for debugging
    Comment(String),
}

impl Instruction {
    /// Return the registers used by this instruction.
    pub fn used_registers(&self) -> Vec<Register> {
        use Instruction::*;

        match self {
            La { dst, src } => Some(*dst).into_iter().chain(src.used_registers()).collect(),
            Ld { dst, src } => Some(*dst).into_iter().chain(src.used_registers()).collect(),
            Sd { dst, src } => dst.used_registers().into_iter().chain(Some(*src)).collect(),
            Arith {
                op: _,
                dst,
                lhs,
                rhs,
            } => vec![*dst, *lhs, *rhs],
            ArithI {
                op: _,
                dst,
                lhs,
                rhs: _,
            } => vec![*dst, *lhs],
            Li { dst, .. } => vec![*dst],
            Jalr { target, dst } => vec![*target, *dst],
            Jal { target: _, dst } => vec![*dst],
            Branch {
                cond: _,
                target: _,
                lhs,
                rhs,
            } => vec![*lhs, *rhs],
            SCmpZ { dst, lhs, cond: _ } => vec![*lhs, *dst],
            Comment(_) => vec![],
        }
    }

    /// Create a jump instruction that does not save the return address.
    pub fn jump(target: JumpTarget) -> Instruction {
        Instruction::Jal { dst: Zero, target }
    }

    /// Create a jump instruction that emulates a direct call using the ra
    /// register for the return address.
    pub fn call(callee: Id) -> Instruction {
        Instruction::Jal {
            dst: Ra,
            target: JumpTarget::Global(callee),
        }
    }

    /// Create an instruction that moves values between registers.
    pub fn mov(dst: Register, src: Register) -> Instruction {
        Instruction::ArithI {
            op: ArithOp::Add,
            dst,
            lhs: src,
            rhs: 0,
        }
    }

    /// Generate a single load instruction from given location to the given
    /// register.  This should generate a move if the source is also a register.
    fn read(dst: Register, src: Location) -> Self {
        match src {
            Reg(r) => Self::mov(dst, r),
            MemoryL(src) => Self::Ld { dst, src },
        }
    }

    /// Generate a single load instruction from given location to the given
    /// register.  This should generate a move if the source is also a register.
    fn write(dst: Location, src: Register) -> Self {
        match dst {
            Reg(r) => Self::mov(r, src),
            MemoryL(dst) => Self::Sd { dst, src },
        }
    }
}

impl std::fmt::Display for Instruction {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        use Instruction::*;

        let target_to_string = |target: &JumpTarget| match target {
            JumpTarget::Local(target) => format!("{target} # local, basic block"),
            JumpTarget::Global(target) => format!("{target} # global, function"),
        };

        match self {
            La { dst, src } => write!(f, "la {dst}, {src}"),
            Ld { dst, src } => write!(f, "ld {dst}, {src}"),
            Sd { dst, src } => write!(f, "sd {src}, {dst}"),
            Li { dst, imm } => write!(f, "li {dst}, {imm}"),
            Arith { op, dst, lhs, rhs } => write!(f, "{op} {dst}, {lhs}, {rhs}"),
            ArithI { op, dst, lhs, rhs } => write!(f, "{op}i {dst}, {lhs}, {rhs}"),
            Jal { dst, target } => write!(f, "jal {dst}, {}", target_to_string(target)),
            Jalr { dst, target } => write!(f, "jalr {dst}, {target}"),
            Branch {
                cond,
                lhs,
                rhs,
                target,
            } => {
                let target = target_to_string(target);
                write!(f, "b{cond} {lhs}, {rhs}, {target}")
            }
            SCmpZ { dst, lhs, cond } => write!(f, "s{cond}z {dst}, {lhs}"),
            Comment(s) => write!(f, "# {s:?}"),
        }
    }
}

/// Conditions for branching
#[derive(Copy, Clone, Eq, PartialEq, Debug, Display)]
enum Condition {
    #[display("eq")]
    Equal,
    #[display("ne")]
    NotEqual,
    #[display("lt")]
    Less,
    #[display("le")]
    LessEq,
    #[display("gt")]
    Greater,
    #[display("ge")]
    GreaterEq,
}

/// Arithmetic operations used in the `Arith` family of instructions.
#[derive(Copy, Clone, Eq, PartialEq, Debug, Display)]
enum ArithOp {
    #[display("add")]
    Add,
    #[display("sub")]
    Sub,
    #[display("mul")]
    Mul,
    #[display("div")]
    Div,
    /// Set if less than given immediate. dst = 1 if lhs < rhs, otherwise dst = 0.
    #[display("slt")]
    Slt,
    #[display("and")]
    And,
    #[display("or")]
    Or,
    #[display("xor")]
    Xor,
    #[display("srl")]
    Srl,
    #[display("sra")]
    Sra,
    #[display("sll")]
    Sll,
}

/// Jump targets.
#[derive(Clone, Eq, PartialEq, Debug)]
enum JumpTarget {
    /// A local jump target in the same function.  These target names are
    /// mangled in the final assembly code so that basic block names in each
    /// function are independent from others.
    Local(Id),
    /// A global jump target.  These targets are used for jumping to global
    /// error handling code.
    Global(Id),
}

struct BasicBlock {
    id: Id,
    instructions: Vec<Instruction>,
}

/// A backend program.
pub struct Program {
    id: Id,
    basic_blocks: Map<Id, BasicBlock>,
    stack_space: i32,
    /// Callee-saved registers used in the main function.  This is used for
    /// generating register save/restore code in function prologue/epilogue.
    used_registers: Vec<Register>,
}

impl Program {
    pub fn asm_code(&self) -> String {
        todo!("generate the final assembly code")
    }
}
