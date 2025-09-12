"""
Weight Sensitivity (Ablation) Experiment for VAC

This script perturbs domain weights for the MEDICAL domain and measures the impact
on composite scores and the key separation sanity checks between truthful,
beneficial, and harmful responses.

Outputs a results folder under experiments/results/ with JSON, CSV, and a
summary.txt.

Usage:
  python -m experiments.ablate_weights --n 5 --scale 0.2
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.vac_evaluator import (
    ValueAlignedConfabulationEvaluator,
    Domain,
    EvaluationContext,
)
from src.evaluation.benchmarks.medical_scenarios import MedicalScenarios


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def evaluate_with_weights(weights: Dict[str, float], limit: int = 0) -> Dict[str, Any]:
    evaluator = ValueAlignedConfabulationEvaluator()
    # Override medical domain weights
    evaluator.domain_weights[Domain.MEDICAL] = weights

    med = MedicalScenarios()
    scenarios = med.scenarios
    if limit and limit > 0:
        scenarios = scenarios[:limit]

    truthful, beneficial, harmful = [], [], []

    for sc in scenarios:
        context = EvaluationContext(
            domain=Domain.MEDICAL,
            user_demographics={"age": "adult"},
            cultural_context="western",
            risk_level=sc.risk_level,
            expert_required=(sc.risk_level in {"high", "critical"}),
            temporal_sensitivity=True,
        )

        if getattr(sc, "ground_truth", None):
            vac = evaluator.evaluate_response(sc.prompt, sc.ground_truth, context)
            truthful.append(vac.composite_score)
        for ex in getattr(sc, "beneficial_confabulation_examples", []) or []:
            vac = evaluator.evaluate_response(sc.prompt, ex, context)
            beneficial.append(vac.composite_score)
        for ex in getattr(sc, "harmful_confabulation_examples", []) or []:
            vac = evaluator.evaluate_response(sc.prompt, ex, context)
            harmful.append(vac.composite_score)

    def _mean(xs: List[float]):
        return sum(xs) / len(xs) if xs else None

    return {
        "weights": weights,
        "means": {
            "truthful": _mean(truthful),
            "beneficial": _mean(beneficial),
            "harmful": _mean(harmful),
        },
        "counts": {
            "truthful": len(truthful),
            "beneficial": len(beneficial),
            "harmful": len(harmful),
        },
        "sanity": {
            "truthful_gt_beneficial": (_mean(truthful) or 0) > (_mean(beneficial) or 0),
            "beneficial_gt_harmful": (_mean(beneficial) or 0) > (_mean(harmful) or 0),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="VAC medical weight ablation experiment")
    parser.add_argument("--n", type=int, default=5, help="Number of random perturbations")
    parser.add_argument("--scale", type=float, default=0.2, help="Perturbation magnitude (0-1)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of scenarios")
    parser.add_argument("--outdir", type=str, default=str(Path("experiments") / "results"))
    args = parser.parse_args()

    base_dir = Path(args.outdir) / f"ablate-weights_{_timestamp()}"
    base_dir.mkdir(parents=True, exist_ok=True)

    evaluator = ValueAlignedConfabulationEvaluator()
    base_weights = deepcopy(evaluator.domain_weights[Domain.MEDICAL])

    import random

    all_results: List[Dict[str, Any]] = []

    # Include baseline (unperturbed)
    all_results.append(evaluate_with_weights(base_weights, limit=args.limit))

    for i in range(args.n):
        w = deepcopy(base_weights)
        # Randomly perturb and renormalize
        for k in w.keys():
            delta = (random.random() * 2 - 1) * args.scale
            w[k] = max(0.0, w[k] + delta)
        # Renormalize to sum to 1
        s = sum(w.values()) or 1.0
        for k in w.keys():
            w[k] = w[k] / s
        all_results.append(evaluate_with_weights(w, limit=args.limit))

    # Save
    with (base_dir / "results.json").open("w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # CSV table
    fields = [
        "weights_alignment",
        "weights_truthfulness",
        "weights_utility",
        "weights_transparency",
        "mean_truthful",
        "mean_beneficial",
        "mean_harmful",
        "sanity_truthful_gt_beneficial",
        "sanity_beneficial_gt_harmful",
    ]
    with (base_dir / "results.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in all_results:
            w.writerow(
                {
                    "weights_alignment": r["weights"].get("alignment"),
                    "weights_truthfulness": r["weights"].get("truthfulness"),
                    "weights_utility": r["weights"].get("utility"),
                    "weights_transparency": r["weights"].get("transparency"),
                    "mean_truthful": r["means"].get("truthful"),
                    "mean_beneficial": r["means"].get("beneficial"),
                    "mean_harmful": r["means"].get("harmful"),
                    "sanity_truthful_gt_beneficial": r["sanity"].get("truthful_gt_beneficial"),
                    "sanity_beneficial_gt_harmful": r["sanity"].get("beneficial_gt_harmful"),
                }
            )

    # Summary text
    baseline = all_results[0]
    with (base_dir / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Baseline weights (MEDICAL):\n")
        f.write(json.dumps(base_weights, indent=2) + "\n\n")
        f.write("Results across perturbations (first row is baseline):\n")
        f.write(json.dumps(all_results, indent=2))

    print(f"Saved ablation results to: {base_dir}")


if __name__ == "__main__":
    main()
