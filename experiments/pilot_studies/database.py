"""Simple local storage for Streamlit value elicitation study.

Saves per-participant sessions under experiments/results/value-elicitation_streamlit.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import uuid

BASE_DIR = Path("experiments") / "results" / "value-elicitation_streamlit"


essential_fields = [
    "participant_id",
    "scenario_id",
    "domain",
    "pair_id",
    "comparison_type",
    "preference",
    "confidence",
    "acceptability_rating",
    "timestamp",
]


def ensure_dir() -> Path:
    ts = datetime.now().strftime("%Y%m%d")
    target = BASE_DIR / ts
    target.mkdir(parents=True, exist_ok=True)
    return target


def new_session_id() -> str:
    return uuid.uuid4().hex[:10]


def save_session_json(participant_id: str, data: Dict[str, Any]) -> Path:
    outdir = ensure_dir()
    fname = outdir / f"{participant_id}_{new_session_id()}.json"
    with fname.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return fname


def append_jsonl(participant_id: str, rows: List[Dict[str, Any]]) -> Path:
    outdir = ensure_dir()
    fname = outdir / f"{participant_id}.jsonl"
    with fname.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    return fname


def finalize_csv(participant_id: str, rows: List[Dict[str, Any]]) -> Path:
    import csv
    outdir = ensure_dir()
    fname = outdir / f"{participant_id}_{new_session_id()}.csv"
    # Flatten rows minimally
    fields = [
        "participant_id",
        "scenario_id",
        "domain",
        "pair_id",
        "comparison_type",
        "preference",
        "confidence",
        "acceptability_response_a",
        "acceptability_response_b",
        "timestamp",
    ]
    with fname.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "participant_id": r.get("participant_id"),
                "scenario_id": r.get("scenario_id"),
                "domain": r.get("domain"),
                "pair_id": r.get("pair_id"),
                "comparison_type": r.get("comparison_type"),
                "preference": r.get("preference"),
                "confidence": r.get("confidence"),
                "acceptability_response_a": r.get("acceptability_rating", {}).get("response_a"),
                "acceptability_response_b": r.get("acceptability_rating", {}).get("response_b"),
                "timestamp": r.get("timestamp"),
            })
    return fname
