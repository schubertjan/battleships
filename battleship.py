import random

ROWS = 9
COLS = 11
FLEET = [
    ("Battleship", 5),
    ("Cruiser", 4),
    ("Destroyer", 3),
    ("Submarine", 3),
    ("PatrolBoat", 2),
]
COL_LABELS = "ABCDEFGHIJK"  # one letter per column (11)


class Board:
    def __init__(self):
        self.ships = []  # list of sets of (row, col)
        self.ship_names = []  # name of each ship, same order as self.ships
        self.occupied = set()  # all ship cells
        self.shots = {}  # (row, col) -> True (hit) / False (miss)

    def can_place(self, cells):
        for r, c in cells:
            if not (0 <= r < ROWS and 0 <= c < COLS):
                return False
            # no ship may be in this cell or any of its 8 neighbours
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (r + dr, c + dc) in self.occupied:
                        return False
        return True

    def place(self, cells, name):
        self.ships.append(set(cells))
        self.ship_names.append(name)
        self.occupied |= set(cells)

    def place_randomly(self):
        for name, length in FLEET:
            while True:
                horizontal = random.random() < 0.5
                # horizontal ships extend along columns, vertical along rows
                r = random.randrange(ROWS - (0 if horizontal else length - 1))
                c = random.randrange(COLS - (length - 1 if horizontal else 0))
                cells = [
                    (r, c + i) if horizontal else (r + i, c) for i in range(length)
                ]
                if self.can_place(cells):
                    self.place(cells, name)
                    break

    def remaining(self):
        """Dict of ship name -> number of its cells not hit yet."""
        return {
            name: sum(1 for cell in ship if not self.shots.get(cell, False))
            for name, ship in zip(self.ship_names, self.ships)
        }

    def fleet_hp(self):
        """Dict of ship name -> hp as the shooter knows it: only sunk ships
        are revealed (0); damage to ships that are still afloat stays hidden,
        so they report their full length."""
        return {
            name: 0 if all(self.shots.get(cell, False) for cell in ship) else len(ship)
            for name, ship in zip(self.ship_names, self.ships)
        }

    def fire(self, pos):
        """Fire at pos. Returns (hit, sunk, fleet_hp):
        hit       - True if a ship was hit
        sunk      - True if this hit sunk a ship, otherwise False
        fleet_hp  - dict of ship name -> hp, where only sunk ships show 0 and
                    every other ship shows its full length (see fleet_hp())
        """
        hit = pos in self.occupied
        self.shots[pos] = hit
        sunk = False
        if hit:
            sunk = any(
                pos in ship and all(self.shots.get(cell, False) for cell in ship)
                for ship in self.ships
            )
        return hit, sunk, self.fleet_hp()

    def all_sunk(self):
        return all(cell in self.shots for cell in self.occupied)

    def render(self, show_ships):
        lines = ["   " + " ".join(COL_LABELS[:COLS])]
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                if (r, c) in self.shots:
                    row.append("X" if self.shots[(r, c)] else "o")
                elif show_ships and (r, c) in self.occupied:
                    row.append("#")
                else:
                    row.append(".")
            lines.append(f"{r + 1:>2} " + " ".join(row))
        return "\n".join(lines)


if __name__ == "__main__":
    board = Board()
    board.place_randomly()
    print(board.render(show_ships=True))
    target = next(iter(board.ships[0]))
    print(target, board.fire(target))
