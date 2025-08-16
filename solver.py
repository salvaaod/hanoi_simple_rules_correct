
from typing import Generator, Tuple

Move = Tuple[int, int]

def hanoi_moves(n: int, src: int = 0, aux: int = 1, dst: int = 2) -> Generator[Move, None, None]:
    if n <= 0:
        return
    yield from hanoi_moves(n-1, src, dst, aux)
    yield (src, dst)
    yield from hanoi_moves(n-1, aux, src, dst)
