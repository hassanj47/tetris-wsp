import numpy as np

def encode(moves):
    x = np.zeros((len(moves),205),np.float32)
    for i, move in enumerate(moves):
        x[i,:200] = move.board.ravel() != 0
        x[i,200+len(move.rows)] = 1
    return x

def forward(x, w):
    with np.errstate(over="raise",invalid="raise"):
        h1 = np.maximum(x @ w["W1"] + w["b1"], 0)
        h2 = np.maximum(h1 @ w["W2"] + w["b2"], 0)
        scores = (h2 @ w["W3"] + w["b3"]).ravel()
    return scores, (x,h1,h2)

def trace(layers, weights, index):
    activations = [layer[index] for layer in layers]
    edges = []
    for depth, activation in enumerate(activations,1):
        matrix = weights[f"W{depth}"]
        values = matrix * activation[:,None]
        # Stable tie order, strongest absolute contributions first.
        order = np.argsort(-np.abs(values.ravel()),kind="stable")[:16]
        layer_edges = []
        for flat in order:
            src,dst = divmod(int(flat),matrix.shape[1])
            if values[src,dst]:
                layer_edges.append(dict(src=src,dst=dst,weight=float(matrix[src,dst]),
                                        value=float(values[src,dst])))
        edges.append(layer_edges)
    return dict(x=activations[0].tolist(),h1=activations[1].tolist(),
                h2=activations[2].tolist(),edges=edges)
