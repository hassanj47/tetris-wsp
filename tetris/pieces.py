"""Spawn masks use screen coordinates. Rotate clockwise, normalize, deduplicate."""
MASKS = dict(I=["IIII"], O=["OO", "OO"], T=[".T.", "TTT"],
             S=[".SS", "SS."], Z=["ZZ.", ".ZZ"], J=["J..", "JJJ"], L=["..L", "LLL"])
IDS = {p: i for i, p in enumerate(MASKS, 1)}


def rotations(mask):
    cells = [(x, y) for y, row in enumerate(mask) for x, c in enumerate(row) if c != "."]
    result = []
    for _ in range(4):
        left, top = min(x for x, y in cells), min(y for x, y in cells)
        shape = tuple(sorted((x-left, y-top) for x, y in cells))
        if shape not in result:
            result.append(shape)
        cells = [(-y, x) for x, y in cells]
    return tuple(result)


SHAPES = {p: rotations(mask) for p, mask in MASKS.items()}
