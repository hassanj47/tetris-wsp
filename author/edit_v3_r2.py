"""Reserve the right edge and value conversion into multi-line clears."""
from author.weight_io import destination, pinned, save


def edit():
    w = pinned('weights/v3_r1.npz', '8dd72dbfc9be03948582fa76f79c01a31c8898f63125fbe43db3730cea0e70ef')
    # Keep the inner surface smooth, but allow the last column to sit lower.
    w['W3'][17] = 0
    w['W2'][109, 21] = 1
    w['W3'][21] = -12
    w['W1'][200:205, 111] = [0, 0, 4, 12, 40]
    return w


if __name__ == '__main__':
    save(destination('weights/v3_r2.npz'), edit())
