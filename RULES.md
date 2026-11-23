# Rules — Astra v3
1. Initial weights are six exact zero float32 arrays. Construct via deterministic reasoning/NumPy.
2. No game before initial artifact is validated and committed.
3. Only three fixed 20-game practice rounds and their supplied outputs are allowed.
4. At most one direct weight edit after each round; max three edits.
5. No training, gradients, optimizers, fitting, RL, evolutionary or random search, sweeps, automated optimization, tree search, minimax, lookahead or rollouts.
6. Never change engine, move generator, RNG, input encoding, network architecture/forward pass, practice harness, seeds, metrics or replay validator.
7. No hand-coded symbolic policy at runtime; all candidate preferences must be encoded in MLP weights.
8. No access to prior WSP artifacts, baselines, heuristic coefficients, expert examples or old replays.
9. No seed-specific hardcoding.
10. Every artifact must be reproducible and hash-pinned.
11. Record each observation, hypothesis, change and round.
12. Report honestly: no zero-shot claim after feedback; no conventional training claim; no unverified neuron semantics; no superiority claim without held-out evidence.