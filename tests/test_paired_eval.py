from tools.paired_eval import (
    aggregate, bootstrap_mean_ci, paired_contrast, piece_sequence_sha256,
    read_json, COHORT_FILE, POLICY_FILE,
)
import numpy as np


def test_cohort_and_policy_manifests_are_fixed():
    cohort = read_json(COHORT_FILE)
    policies = read_json(POLICY_FILE)
    assert cohort["count"] == 50
    assert len(cohort["seeds"]) == len(set(cohort["seeds"])) == 50
    assert cohort["seeds"] == sorted(cohort["seeds"])
    assert len(policies) == 6
    assert len({p["id"] for p in policies}) == 6


def test_piece_sequence_hash_is_deterministic():
    assert piece_sequence_sha256(12345) == piece_sequence_sha256(12345)
    assert piece_sequence_sha256(12345) != piece_sequence_sha256(12346)


def test_bootstrap_ci_for_zero_differences_is_zero():
    ci = bootstrap_mean_ci([0.0] * 10, np.random.default_rng(7))
    assert ci == [0.0, 0.0]


def test_paired_contrast_preserves_seed_matching():
    left = [{"seed": 1, "score": 20, "lines": 2, "pieces": 10},
            {"seed": 2, "score": 30, "lines": 3, "pieces": 12}]
    right = [{"seed": 1, "score": 10, "lines": 1, "pieces": 8},
             {"seed": 2, "score": 30, "lines": 2, "pieces": 12}]
    result = paired_contrast(left, right, np.random.default_rng(9))
    assert result["score"]["mean_difference_left_minus_right"] == 5
    assert result["score_win_tie_loss"] == {"left_wins": 1, "ties": 1, "right_wins": 0}


def test_aggregate_counts_caps_and_clear_events():
    games = [
        {"score": 100, "lines": 2, "pieces": 10, "capped": False,
         "singles": 1, "doubles": 0, "triples": 0, "tetrises": 0,
         "mean_stack_height": 3.0, "max_stack_height": 8, "column_9_empty_fraction": 0.5},
        {"score": 300, "lines": 4, "pieces": 20, "capped": True,
         "singles": 0, "doubles": 0, "triples": 0, "tetrises": 1,
         "mean_stack_height": 5.0, "max_stack_height": 10, "column_9_empty_fraction": 0.25},
    ]
    result = aggregate(games)
    assert result["mean_score"] == 200
    assert result["cap_games"] == 1
    assert result["clear_events"]["tetrises"] == 1
    assert result["tetrises_per_game"] == 0.5
