"""Fixed, nonoverlapping seed ranges shared by the evaluation and recording CLIs."""
COHORTS = {"development": range(0, 10_000), "refinement": range(10_000, 10_060),
           "held-out": range(20_000, 20_100)}


def validate_seeds(name, seeds):
    allowed = COHORTS[name]
    if len(set(seeds)) != len(seeds) or any(seed not in allowed for seed in seeds):
        raise ValueError(f"{name} requires distinct seeds in [{allowed.start}, {allowed.stop})")
