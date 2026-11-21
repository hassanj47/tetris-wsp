# AGENTS.md — Codex Builder Instructions

## Your role

You are the **Builder**, not the WSP Author or WSP Editor.

Implement the Tetris engine, fixed neural inference runtime, baselines, evaluation/replay tools, tests, static two-panel viewer, and project documentation according to `PLAN.md`.

## Mandatory boundaries

1. Read `PLAN.md`, `RULES.md`, and `author_brief/BRIEF.md` before implementation.
2. Follow the exact game rules, input encoding, architecture, tensor shapes, and replay requirements.
3. Do not generate experimental v1 or v2 neural weights.
4. Do not author or edit the experimental neural policy weights.
5. Do not use training, gradients, optimizers, evolutionary algorithms, random search, or parameter tuning to create a controller.
6. Do not put heuristic implementation details or baseline results in `author_brief/`.
7. Keep Author and Editor workspaces isolated as specified in `PLAN.md`.
8. Never fabricate Astra-generated weights, activations, logs, evaluation results, or transcripts.
9. Synthetic/mock fixtures may be used only to test the viewer before real weights exist. Label them unmistakably as test fixtures and never include them in experimental results.
10. The project is replay-first. Python executes simulations in Codex Cloud; the static browser viewer renders recorded data.

## Implementation priorities

1. Correctness and determinism of the engine.
2. Exact and tested MLP inference implementation.
3. Reproducible candidate generation and evaluation.
4. Self-contained replay schema.
5. Viewer that renders actual replay data.
6. Sleek neural visualization with real activations.
7. Static deployment through GitHub Pages.
8. Documentation and reproducible commands.

## Visualization requirements

- Default layout: Tetris gameplay on the left, animated neural network on the right.
- Aim for a polished dark interface suitable for a 1920×1080 recording.
- Use SVG or Canvas for the neural network.
- Take inspiration from 3Blue1Brown/Manim-style explanatory animation: clarity, restrained motion, mathematically meaningful transitions.
- Do not copy assets, branding, or exact compositions.
- Show the real architecture: 205 inputs, 128 hidden neurons, 32 hidden neurons, one scalar output.
- Abstract/group the 205 inputs to preserve legibility.
- Animate actual recorded activations.
- Highlight only actual weighted contributions derived from the weights and activations.
- Heatmaps are a secondary inspection mode, never the default visual.
- Do not use raw Matplotlib or Seaborn plots as the main UI.

## Engineering requirements

- Keep dependencies minimal: NumPy and pytest for Python.
- Prefer readable, modular code.
- Add tests for important game and inference behavior.
- Use deterministic seeds everywhere randomness is involved.
- Validate shapes, dtypes, and finite values for all weight tensors.
- Make replay schema explicit and versioned.
- Make the viewer work without a backend or runtime API.
- Add a GitHub Pages Actions workflow that publishes `viewer/`.
- Do not claim deployment is complete until repository settings and the published URL have been verified.

## Work process

- First inspect the repository and summarize the implementation plan.
- Implement in small, testable steps.
- Run tests after meaningful changes.
- Document commands and any environment assumptions.
- If a requirement is ambiguous, prefer the least complex implementation that preserves experimental validity and document the decision.
- Do not silently change the architecture or experiment protocol.
- If the exact specification is impossible or inconsistent, explain the issue and propose the smallest correction before proceeding.

## Stop condition

Stop after completing Builder Phases 1 and 2 in `PLAN.md`.

At handoff, report:
- files created/changed;
- tests and exact results;
- how to run evaluation and generate replays;
- how to open the viewer locally;
- how GitHub Pages deployment is configured;
- remaining blockers;
- confirmation that no experimental v1/v2 weights were generated.

Do not proceed to Author or Editor phases.
