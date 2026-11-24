import argparse
import itertools
import random
import sqlite3

import battleship

ROWS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
COLS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
COLS_ROWS = [item[1] + item[0] for item in list(itertools.product(ROWS, COLS))]
SCHEMA = f"""
DROP TABLE IF EXISTS moves;
CREATE TABLE moves (
    id          INTEGER PRIMARY KEY,
    {", ".join([col + row + "   INTEGER NOT NULL" for row in ROWS for col in COLS])},
    {", ".join([ship[0] + "   INTEGER NOT NULL" for ship in battleship.FLEET])},
    rc          INTEGER NOT NULL
);
"""

# Cell states
NOT_USED, MISS, HIT = 0, 1, 2
# Ship columns: 0 = not sunk, 1 = sunk
DEFAULT_FLEET_SUNK = {ship[0]: 0 for ship in battleship.FLEET}


def play_game():
    """Play one random game. Returns the list of recorded moves (hits only)."""
    board = battleship.Board()
    board.place_randomly()
    shot_order = [
        (c, r) for r in range(battleship.ROWS) for c in range(battleship.COLS)
    ]
    random.shuffle(shot_order)

    state = [NOT_USED] * (battleship.ROWS * battleship.COLS)
    moves = []
    known_fleet_sunk = DEFAULT_FLEET_SUNK
    for c, r in shot_order:
        hit, ship_sunk, ships_hp = board.fire((r, c))
        result = 1 if hit else 0
        if result == 1:
            moves.append(
                {"id": None}
                | {col: value for col, value in (zip(COLS_ROWS, state))}
                | known_fleet_sunk
                | {"rc": f"{COLS[c]}{ROWS[r]}"}
            )
        state[r * battleship.COLS + c] = HIT if hit else MISS
        if ship_sunk:
            # 1 = sunk, 0 = not sunk (a ship with hp 0 is sunk)
            known_fleet_sunk = {name: int(hp == 0) for name, hp in ships_hp.items()}
        if board.all_sunk():
            break
    return moves


def main():
    ap = argparse.ArgumentParser(
        description="Simulate random Battleship games into SQLite."
    )
    ap.add_argument(
        "--games", type=int, default=100, help="number of games to play (X)"
    )
    ap.add_argument(
        "--db", default="battleship.db", help="SQLite file (default: battleship.db)"
    )
    ap.add_argument(
        "--seed", type=int, default=42, help="base seed for reproducible runs"
    )
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.executescript(SCHEMA)
    cur = con.cursor()

    total = 0
    for i in range(args.games):
        seed = None if args.seed is None else args.seed + i
        if seed is not None:
            random.seed(seed)
        moves = play_game()

        cols = [f":{key}" for key in moves[0].keys()]
        cur.executemany(f"INSERT INTO moves VALUES ({", ".join(cols)})", moves)
        total += len(moves)
        if (i + 1) % 100 == 0:
            con.commit()
            print(f"  {i + 1}/{args.games} games...")
    con.commit()
    con.close()

    print(f"Done: {args.games} games saved to {args.db}")


if __name__ == "__main__":
    main()
