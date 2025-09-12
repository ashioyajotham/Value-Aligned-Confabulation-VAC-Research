"""
Run Medical Benchmark Experiments for VAC

This script evaluates the VAC framework on all medical benchmark scenarios and
computes sanity-check metrics that should hold if the framework behaves as intended:
- Truthful > Beneficial Confabulation > Harmful Confabulation on average
- Sensitivity to scenario risk level (higher risk => lower tolerance)

Outputs:
- A timestamped results folder under experiments/results/
- JSON with per-item detailed scores
- CSV with flattened results
- Printed summary and sanity-check pass rates

Usage (from project root):
  python -m experiments.run_medical_benchmark --limit 0 --outdir experiments/results

Or directly:
  python experiments/run_medical_benchmark.py --limit 0 --outdir experiments/results
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

# Make project root importable (so "src" package resolves) when run directly
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


def build_context(risk_level: str) -> EvaluationContext:
    return EvaluationContext(
        domain=Domain.MEDICAL,
        user_demographics={"age": "adult", "medical_knowledge": "layperson"},
        cultural_context="western",
        risk_level=risk_level,
        expert_required=(risk_level in {"high", "critical"}),
        temporal_sensitivity=True,
    )


def evaluate_all(limit: int = 0) -> Dict[str, Any]:
    evaluator = ValueAlignedConfabulationEvaluator()
    med = MedicalScenarios()

    scenarios = med.scenarios
    if limit and limit > 0:
        scenarios = scenarios[:limit]

    detailed: List[Dict[str, Any]] = []

    # For risk sensitivity aggregation
    by_risk: Dict[str, List[float]] = {"critical": [], "high": [], "medium": [], "low": []}

    # Accumulators for separation sanity checks
    truthful_scores: List[float] = []
    beneficial_scores: List[float] = []
    harmful_scores: List[float] = []

    pairwise_correct_truthful_vs_beneficial = 0
    pairwise_correct_beneficial_vs_harmful = 0
    total_pairs_tb = 0
    total_pairs_bh = 0

    for sc in scenarios:
        context = build_context(sc.risk_level)

        responses = []
        # Truthful
        if getattr(sc, "ground_truth", None):
            responses.append(("truthful", sc.ground_truth))
        # Beneficial confab examples
        for ex in getattr(sc, "beneficial_confabulation_examples", []) or []:
            responses.append(("beneficial", ex))
        # Harmful confab examples
        for ex in getattr(sc, "harmful_confabulation_examples", []) or []:
            responses.append(("harmful", ex))

        type_to_score: Dict[str, List[float]] = {"truthful": [], "beneficial": [], "harmful": []}

        for rtype, text in responses:
            vac = evaluator.evaluate_response(sc.prompt, text, context)
            type_to_score[rtype].append(vac.composite_score)

            detailed.append(
                {
                    "scenario_id": getattr(sc, "id", None) or sc.prompt[:48],
                    "risk_level": sc.risk_level,
                    "vac_tolerance": getattr(sc, "expected_vac_tolerance", None),
                    "response_type": rtype,
                    "prompt": sc.prompt,
                    "response": text,
                    "alignment": vac.alignment_score,
                    "truthfulness": vac.truthfulness_score,
                    "utility": vac.utility_score,
                    "transparency": vac.transparency_score,
                    "composite": vac.composite_score,
                }
            )

        # Aggregate per-scenario sanity checks
        if type_to_score["truthful"]:
            t = sum(type_to_score["truthful"]) / len(type_to_score["truthful"])
            truthful_scores.append(t)
            by_risk[sc.risk_level].append(t)
        if type_to_score["beneficial"]:
            b = sum(type_to_score["beneficial"]) / len(type_to_score["beneficial"])
            beneficial_scores.append(b)
            by_risk[sc.risk_level].append(b)
        if type_to_score["harmful"]:
            h = sum(type_to_score["harmful"]) / len(type_to_score["harmful"])
            harmful_scores.append(h)
            by_risk[sc.risk_level].append(h)

        # Pairwise checks: use means per type for this scenario
        if type_to_score["truthful"] and type_to_score["beneficial"]:
            total_pairs_tb += 1
            if (sum(type_to_score["truthful"]) / len(type_to_score["truthful"])) > (
                sum(type_to_score["beneficial"]) / len(type_to_score["beneficial"]) 
            ):
                pairwise_correct_truthful_vs_beneficial += 1
        if type_to_score["beneficial"] and type_to_score["harmful"]:
            total_pairs_bh += 1
            if (sum(type_to_score["beneficial"]) / len(type_to_score["beneficial"])) > (
                sum(type_to_score["harmful"]) / len(type_to_score["harmful"]) 
            ):
                pairwise_correct_beneficial_vs_harmful += 1

    # Summaries
    summary = {
        "n_scenarios": len(scenarios),
        "count_truthful": len(truthful_scores),
        "count_beneficial": len(beneficial_scores),
        "count_harmful": len(harmful_scores),
        "mean_truthful": (sum(truthful_scores) / len(truthful_scores)) if truthful_scores else None,
        "mean_beneficial": (sum(beneficial_scores) / len(beneficial_scores)) if beneficial_scores else None,
        "mean_harmful": (sum(harmful_scores) / len(harmful_scores)) if harmful_scores else None,
        "pairwise_accuracy_truthful_gt_beneficial": (
            pairwise_correct_truthful_vs_beneficial / total_pairs_tb if total_pairs_tb else None
        ),
        "pairwise_accuracy_beneficial_gt_harmful": (
            pairwise_correct_beneficial_vs_harmful / total_pairs_bh if total_pairs_bh else None
        ),
        "risk_level_means": {
            k: (sum(v) / len(v) if v else None) for k, v in by_risk.items()
        },
    }

    return {"summary": summary, "details": detailed}


def save_results(results: Dict[str, Any], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    # JSON
    with (outdir / "results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # CSV (flattened)
    fields = [
        "scenario_id",
        "risk_level",
        "vac_tolerance",
        "response_type",
        "composite",
        "alignment",
        "truthfulness",
        "utility",
        "transparency",
        "prompt",
        "response",
    ]
    with (outdir / "results.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in results.get("details", []):
            w.writerow({k: row.get(k) for k in fields})

    # Summary text
    with (outdir / "summary.txt").open("w", encoding="utf-8") as f:
        json.dump(results.get("summary", {}), f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Run VAC medical benchmark experiments")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of scenarios (0 = all)")
    parser.add_argument(
        "--outdir",
        type=str,
        default=str(Path("experiments") / "results"),
        help="Base output directory",
    )
    args = parser.parse_args()

    # Build output dir with timestamp
    base = Path(args.outdir)
    outdir = base / f"medical-benchmark_{_timestamp()}"

    results = evaluate_all(limit=args.limit)

    print("\n==== VAC Medical Benchmark Summary ====")
    print(json.dumps(results["summary"], indent=2))

    save_results(results, outdir)
    print(f"\nSaved results to: {outdir}")


if __name__ == "__main__":
    main()
