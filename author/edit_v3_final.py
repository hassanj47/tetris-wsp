"""Retain a shallow right-edge scoring opportunity with a depth limit."""
from author.weight_io import destination, pinned, save


def edit():
    w = pinned('weights/v3_r2.npz', '9356129a51335e306a29f058b99d40633dd66dd82cc29a19d512b9737396a127')
    # Each occupied edge cell costs one instead of twelve. A shallow edge
    # costs half the normal surface penalty; beyond depth three add two.
    w['W3'][21] = -1
    w['W3'][17] = -0.5
    w['W2'][:, 22] = w['W2'][:, 17]
    w['b2'][22] = -3
    w['W3'][22] = -2
    w['W1'][200:205, 111] = [0, 2, 6, 12, 24]
    return w


if __name__ == '__main__':
    save(destination('weights/v3_final.npz'), edit())
