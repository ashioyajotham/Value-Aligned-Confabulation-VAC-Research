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
    # Validate inputs for cloud environment
    if not participant_id or participant_id.strip() == "":
        participant_id = f"unknown_{uuid.uuid4().hex[:8]}"
    if not data:
        data = {"error": "No data provided", "timestamp": datetime.now().isoformat()}
    
    outdir = ensure_dir()
    fname = outdir / f"{participant_id}_{new_session_id()}.json"
    with fname.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return fname


def append_jsonl(participant_id: str, rows: List[Dict[str, Any]]) -> Path:
    # Validate inputs for cloud environment
    if not participant_id or participant_id.strip() == "":
        participant_id = f"unknown_{uuid.uuid4().hex[:8]}"
    if not rows:
        rows = [{"error": "No rows provided", "timestamp": datetime.now().isoformat()}]
    
    outdir = ensure_dir()
    fname = outdir / f"{participant_id}.jsonl"
    with fname.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    return fname


def finalize_csv(participant_id: str, rows: List[Dict[str, Any]]) -> Path:
    import csv
    
    # Validate inputs for cloud environment
    if not participant_id or participant_id.strip() == "":
        participant_id = f"unknown_{uuid.uuid4().hex[:8]}"
    if not rows:
        rows = [{"error": "No rows provided", "timestamp": datetime.now().isoformat()}]
    
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
        "study_id",
        "study_version",
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
                "study_id": r.get("study_id"),
                "study_version": r.get("study_version"),
                "acceptability_response_a": r.get("acceptability_rating", {}).get("response_a"),
                "acceptability_response_b": r.get("acceptability_rating", {}).get("response_b"),
                "timestamp": r.get("timestamp"),
            })
    return fname


def get_all_data_files() -> Dict[str, List[Path]]:
    """Get all stored data files organized by type."""
    files = {"json": [], "jsonl": [], "csv": []}
    
    if not BASE_DIR.exists():
        return files
    
    # Scan all date subdirectories
    for date_dir in BASE_DIR.glob("*"):
        if date_dir.is_dir():
            files["json"].extend(date_dir.glob("*.json"))
            files["jsonl"].extend(date_dir.glob("*.jsonl"))
            files["csv"].extend(date_dir.glob("*.csv"))
    
    return files


def aggregate_all_jsonl_data() -> List[Dict[str, Any]]:
    """Read and combine all JSONL files into a single list."""
    all_data = []
    files = get_all_data_files()
    
    for jsonl_file in files["jsonl"]:
        try:
            with jsonl_file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            all_data.append(data)
                        except json.JSONDecodeError:
                            continue
        except Exception:
            continue
    
    return all_data


def create_download_csv(data: List[Dict[str, Any]]) -> str:
    """Convert aggregated data to CSV string for download."""
    import csv
    import io
    
    if not data:
        return ""
    
    output = io.StringIO()
    fields = [
        "participant_id", "scenario_id", "domain", "pair_id", 
        "comparison_type", "preference", "confidence", "study_id", 
        "study_version", "acceptability_response_a", "acceptability_response_b", 
        "timestamp"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    
    for row in data:
        writer.writerow({
            "participant_id": row.get("participant_id"),
            "scenario_id": row.get("scenario_id"),
            "domain": row.get("domain"),
            "pair_id": row.get("pair_id"),
            "comparison_type": row.get("comparison_type"),
            "preference": row.get("preference"),
            "confidence": row.get("confidence"),
            "study_id": row.get("study_id"),
            "study_version": row.get("study_version"),
            "acceptability_response_a": row.get("acceptability_rating", {}).get("response_a"),
            "acceptability_response_b": row.get("acceptability_rating", {}).get("response_b"),
            "timestamp": row.get("timestamp"),
        })
    
    return output.getvalue()


def get_data_summary() -> Dict[str, Any]:
    """Get summary statistics for admin dashboard."""
    all_data = aggregate_all_jsonl_data()
    
    if not all_data:
        return {
            "total_responses": 0,
            "unique_participants": 0,
            "recent_activity": [],
            "domain_counts": {}
        }
    
    # Count unique participants
    participants = set()
    domain_counts = {}
    recent_activity = []
    
    for row in all_data:
        if "participant_id" in row:
            participants.add(row["participant_id"])
        
        # Count by domain
        domain = row.get("domain", "unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Track recent activity (last 10 responses)
        if len(recent_activity) < 10:
            recent_activity.append({
                "participant": row.get("participant_id", "unknown")[:12],
                "timestamp": row.get("timestamp", ""),
                "domain": domain
            })
    
    return {
        "total_responses": len(all_data),
        "unique_participants": len(participants),
        "recent_activity": recent_activity,
        "domain_counts": domain_counts
    }
