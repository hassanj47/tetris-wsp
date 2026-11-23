"""Count open sky in row pairs to measure true height and buried air."""
from author.weight_io import destination, pinned, save


def edit():
    w = pinned('weights/v3_initial.npz', 'bfe47746692c6f602da68e580dd4b92bdb62b4ea833a008b8552ae51f6e2feaf')
    for pair in range(10):
        lower = 2 * pair + 1
        for col in range(10):
            unit = pair * 10 + col
            w['W1'][:, unit] = 0
            w['W1'][col:10 * lower:10, unit] = -2
            w['W1'][10 * lower + col, unit] = -1
            w['b1'][unit] = 2
            # Paired sky count is 0, 1 or 2. Summing over pairs gives
            # sky length; either sign can feed absolute height differences.
            w['W2'][unit, 0] = -1
            if col < 9:
                w['W2'][unit, 1 + 2 * col:3 + 2 * col] = [-1, 1]
            if col > 0:
                w['W2'][unit, 2 * col - 1:2 * col + 1] = [1, -1]
    w['W2'][100:110, 1:19] = 0
    w['W2'][100:110, 0] = -1
    w['b2'][0] = 200
    # One two-cell cavity now counts twice; a unit cost of ten retains
    # a large penalty while allowing the score to trade a small cavity.
    w['W3'][0] = -10
    return w


if __name__ == '__main__':
    save(destination('weights/v3_r1.npz'), edit())
