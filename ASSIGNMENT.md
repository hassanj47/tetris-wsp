# Astra Author · initial v1

Start a fresh Astra session with this directory as its only project input. Read RULES.md and author_brief/BRIEF.md. Directly construct all 30,529 parameters of the specified placement-scoring MLP using deterministic Python and NumPy. Reason from the brief alone. No training, gradients, optimization, weight search, baseline information, gameplay, or evaluation feedback. Stop at the initial artifact.

Produce author/build_v1.py, weights/v1.npz, weights/v1_labels.json, author/LOG.md and author/v1_provenance.json. Describe intended neuron roles as hypotheses. Validate all six named tensors against the brief, including exact shapes, float32 dtype and finiteness. Re-run the script and verify identical tensors. Record the model/session, prompt, input files, method, software versions, exact reproduction command, zero evaluations, and SHA-256 hashes of the script, weights and labels. Retain the original outputs for the operator.
