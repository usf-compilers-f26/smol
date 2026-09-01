//! This is the compiler as a library.  See `src/bin` directory for the
//! executable programs using this library.

// Because this is a library, allow dead code to make in-class exercises easier
// to develop.
#![allow(dead_code)]

pub mod back;
pub mod common;
pub mod front;
pub mod middle;
