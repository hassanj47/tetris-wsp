# Cloud-only Astra Author workspace

This branch is an intentionally isolated workspace for the initial v1 weight-space authoring attempt.

## Scope and isolation
- Treat only the checked-out files in this branch as available project inputs.
- Do not inspect git history, parent commits, other branches, pull requests, issues, or other repositories.
- Do not access or reconstruct Builder code, policies, baselines, evaluation reports, replay recordings, or previous experiments.
- Do not use the network or web search to obtain alternative solutions.
- Do not launch subagents or delegate this task.

## Required method
- Follow ASSIGNMENT.md, RULES.md, and author_brief/BRIEF.md exactly.
- Construct all six tensors directly using deterministic reasoning and NumPy.
- Do not train, optimize, search weights, run gameplay, run a policy, or evaluate performance.
- Static checks only: exact tensor names/shapes, float32 dtype, finite values, deterministic reproduction, and SHA-256 provenance.

## Outputs
Create exactly the required deliverables:
- author/build_v1.py
- weights/v1.npz
- weights/v1_labels.json
- author/LOG.md
- author/v1_provenance.json

Commit the completed artifacts to this branch only. Do not open a pull request or merge anything.
