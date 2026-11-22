# Codex Builder Task — Implement the Tetris WSP Demo

You are working in the `tetris-wsp` repository.

Read `AGENTS.md`, `PLAN.md`, `RULES.md`, and `author_brief/BRIEF.md` first. Treat them as the project specification.

## Assignment

Implement Builder Phases 1 and 2 only:

1. deterministic Tetris engine and move generation;
2. fixed NumPy MLP inference runtime and strict artifact validation;
3. random and conventional heuristic baselines;
4. evaluation and reporting tools;
5. replay recording with actual inference activations;
6. weight dump, weight diff, and authoring-rule checks;
7. polished static two-panel viewer;
8. synchronized v1/v2 comparison mode;
9. complete tests and documentation;
10. GitHub Pages deployment workflow.

## Critical boundaries

- Do not generate the experimental v1 or v2 weights.
- Do not attempt WSP synthesis or editing.
- Do not train or optimize any network.
- Do not fabricate experimental results, real Astra activations, or transcripts.
- You may use clearly labeled synthetic fixtures only to test the viewer before actual WSP artifacts exist.
- Keep the Author and Editor workspaces isolated as specified.
- Stop after Builder Phase 2 and provide a handoff report.

## Visual requirement

The viewer is a central deliverable, not an afterthought.

Create a polished dark-mode interface suitable for a 1920×1080 LinkedIn recording:
- left: Tetris gameplay;
- right: sleek animated neural network;
- synchronized playback and candidate decision display;
- actual recorded activations and weighted contributions;
- compact secondary weight-inspection view;
- v1/v2 compare mode.

The default neural view should take inspiration from 3Blue1Brown/Manim-style explanatory animation: mathematically meaningful, elegant, clear, and smooth. Do not copy assets or branding. Do not use a raw heatmap as the default. Heatmaps are optional secondary inspection tools.

The network diagram must correspond to the actual 205 → 128 → 32 → 1 architecture. The 205 inputs should be abstracted/grouped for legibility. Hidden layers should be represented faithfully. Any highlighted connections must be derived from actual weights and recorded activations.

## Replay-first architecture

Python + NumPy executes in Codex Cloud. Record self-contained replay data. The browser viewer is static HTML/CSS/JavaScript and must not require a backend, Python process, Codex session, or runtime API.

Add a GitHub Pages workflow publishing `viewer/`.

## Required final handoff

Before stopping:
- run all tests;
- report exact test results;
- document commands for evaluation and replay generation;
- document how to preview the viewer;
- verify static build/deployment configuration;
- list files changed;
- state any remaining limitations;
- explicitly confirm that no experimental v1/v2 weights were generated.

Do not continue to the Author or Editor phases.
