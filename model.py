
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

Move = Tuple[int, int]  # (from_peg, to_peg)

@dataclass
class GameState:
    n_disks: int = 4
    pegs: List[List[int]] = field(default_factory=lambda: [[], [], []])
    selected_peg: Optional[int] = None
    moves_made: int = 0

    def __post_init__(self):
        # Internal invariant:
        # - Each peg list is ordered from bottom -> top
        # - The TOP is the LAST element (list[-1]) so pop/append are O(1)
        # - Disk numbers: 1 = smallest ... n = largest
        # Initial left peg: [n, n-1, ..., 1]
        if not any(self.pegs):
            self.pegs = [list(range(self.n_disks, 0, -1)), [], []]

    def reset(self, n: Optional[int] = None):
        if n is not None:
            if n < 1 or n > 8:
                raise ValueError("n must be 1..8")
            self.n_disks = n
        self.pegs = [list(range(self.n_disks, 0, -1)), [], []]
        self.selected_peg = None
        self.moves_made = 0

    def can_move(self, src: int, dst: int) -> bool:
        if src == dst:
            return False
        if not self.pegs[src]:
            return False  # no disk to move
        if not self.pegs[dst]:
            return True   # can always move onto empty peg
        # Only smaller (top of src) onto larger (top of dst)
        return self.pegs[src][-1] < self.pegs[dst][-1]

    def move(self, src: int, dst: int) -> bool:
        if self.can_move(src, dst):
            disk = self.pegs[src].pop()
            self.pegs[dst].append(disk)
            self.moves_made += 1
            return True
        return False

    def is_solved(self) -> bool:
        # With legal moves only, all disks on right peg implies sorted ascending top
        return len(self.pegs[2]) == self.n_disks
