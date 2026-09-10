## How it works

The solver builds a puzzle in two stages:

1. **Kernel puzzle**: a small starting puzzle (5x5) is solved completely — border first
   (`old_border_solver.py`), then interior pieces (`middle_solver.py`) — using constraint
   satisfaction: each piece is a CSP variable, its domain is the positions/rotations still
   available to it, and backtracking search fills the grid with forward checking (placing a
   piece immediately trims neighboring pieces' domains) and a minimum-remaining-values-style
   heuristic (place whichever piece has the fewest options left, tie-broken by how many of
   its neighbors are already placed).

2. **Ring expansion**: each valid kernel solution is grown by wrapping a new ring of border
   pieces around it (`BorderWrap/border_solver.py`), turning the 5x5 kernel into a 7x7
   puzzle without disturbing the interior that's already solved. This step uses the same
   CSP/backtracking approach and is designed to repeat for further growth (7x7 -> 9x9, per
   a reference file already in the repo).

The two-solutions requirement is enforced throughout by solving two independent valid
arrangements (`grid1` and `grid2`) of the same piece set together, rather than finding one
solution and searching for a second afterward.

## Project structure

The current implementation is in `Python/`:
- `main.py` — entry point; solves the initial kernel, then wraps new border rings around it
  to grow the puzzle.
- `old_border_solver.py` — solves the initial kernel puzzle's border. (Named "old" from
  development history, not from being superseded — it's the active kernel-border solver.)
- `middle_solver.py` — solves interior (non-border) pieces, used for the kernel and for
  interior fill during growth.
- `BorderWrap/border_solver.py` — wraps a new border ring around an already-solved grid to
  grow it (5x5 -> 7x7 -> ...).
- `compare.py`, `main_old.py` — not part of the active pipeline. `main_old.py` is dead code
  from an earlier version. `compare.py` was a migration aid used to diff the JS version's
  output against the Python port's while the Python rewrite was catching up on missing
  solutions; kept for reference now that the migration is complete.

The HTML/JS files at the repository root are earlier prototype versions built before the
project moved to Python; the active implementation is the one described above.

