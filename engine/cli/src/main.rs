//! `twomove` — line-protocol engine binary that `twomove/arena.py` drives, one
//! child process per worker. Protocol spec: engine/PROTOCOL.md.
//!
//! Status: skeleton. Parses the framing and answers `ping` / `quit` / `id`;
//! `newgame` / `position` / `go` are stubbed until the core port lands.

use std::io::{self, BufRead, Write};

const NAME: &str = "twomove";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn main() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut out = stdout.lock();

    for line in stdin.lock().lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => break,
        };
        let mut it = line.split_whitespace();
        let cmd = it.next().unwrap_or("");
        match cmd {
            "" => {}
            "ping" => {
                let _ = writeln!(out, "pong {}", it.next().unwrap_or(""));
            }
            "id" => {
                let _ = writeln!(out, "id name {NAME} {VERSION}");
            }
            "quit" | "exit" => break,
            "newgame" | "position" | "go" => {
                // TODO(port): wire twomove_core::{rules, turn, search}.
                let _ = writeln!(out, "error unimplemented {cmd}");
            }
            other => {
                let _ = writeln!(out, "error unknown-command {other}");
            }
        }
        let _ = out.flush();
    }
}
