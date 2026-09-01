//! The back-end of the compiler.

pub mod asm;
pub mod codegen;

pub use asm::*;
pub use codegen::*;

#[cfg(test)]
mod tests;
