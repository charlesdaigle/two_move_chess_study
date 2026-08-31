# twomove engine line protocol (draft v0)

One `twomove` child process per `arena.py` worker. Line-based, `\n`-terminated,
UTF-8. Engine reads stdin, writes stdout; stderr is logs only. All coordinates
are `file,rank` 0-based (`a1` = `0,0`); half-moves are `from-to[=promo]` e.g.
`4,1-4,3` or `4,6-4,7=Q`.

## Handshake
```
-> id
<- id name twomove <version>
-> ping 42
<- pong 42
```

## Per game
```
-> newgame <ruleset-json>
<- ok
-> position startpos
   position halfmoves <hm> <hm> ...      # from the material scheme's start
<- ok
-> go nodes 12000 seed 12345
<- bestmove 4,1-4,3
```
`<ruleset-json>` mirrors `twomove/rules.py: Ruleset` — `double_color`,
`first_player`, `check_regime` (KC|ET|IL), `nc2`, `dp2`, `k`, `cap`, `material`
(scheme name or an explicit placement map), plus `geometry` `{files, ranks}` and
a `pieces` table for fairy kinds.

The engine tracks the turn schedule itself; `go` always asks for the single
half-move the current mover should play now. `arena.py` applies it, then either
asks `go` again (second half of a double turn) or hands the turn over.

## Notes
- Deterministic given `(ruleset, halfmoves, nodes, seed)` — this is what makes
  recorded games replayable and shards independent.
- Errors: `error <slug> [detail]`, engine stays alive for the next `newgame`.
- `quit` ends the process.

Status: only `id` / `ping` / `quit` implemented. The rest is stubbed pending the
core port (engine/README.md steps 1-5).
