# Viewer

This directory contains the static browser application deployed by GitHub Pages.

The viewer must:
- load replay JSON from `data/manifest.json`;
- render Tetris gameplay on the left;
- render the actual neural network and recorded activations on the right;
- support synchronized replay and v1/v2 comparison;
- work without a backend, Python runtime, Codex session, or external API.

The default neural view should be a polished, explanatory SVG/Canvas animation inspired by the clarity and motion language of 3Blue1Brown/Manim-style explainers. It must use actual replay activations and model data. A weight heatmap is a secondary inspection view only.

The Builder should replace the temporary `index.html` with the completed application.
