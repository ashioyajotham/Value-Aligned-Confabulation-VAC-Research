"""Streamlit UI for the Value Elicitation Pilot Study.
Run with:
  streamlit run experiments/pilot_studies/streamlit_app.py
"""
from __future__ import annotations

import random
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import uuid

import streamlit as st

# Local imports
from .value_elicitation_study import ValueElicitationStudy
from .database import save_session_json, append_jsonl, finalize_csv
from .config import ASCII_BANNER, APP_TITLE, PRIMARY_COLOR, ACCENT_COLOR, MUTED_TEXT, INTRO_MD, FOOTER_TEXT

# Basic page config and styles
st.set_page_config(page_title=APP_TITLE, page_icon="🧪", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }}
    .vac-header {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        color: {PRIMARY_COLOR};
        white-space: pre;
        font-size: 12px;
        line-height: 12px;
        margin-bottom: 0.5rem;
    }}
    .vac-subtitle {{ color: {MUTED_TEXT}; margin-bottom: 1rem; }}
    .vac-card {{
        border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; background: #ffffff;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }}
    .vac-footer {{ color: {MUTED_TEXT}; font-size: 12px; margin-top: 2rem; }}
    .pref-a {{ background: rgba(79,70,229,0.05); padding: 8px; border-radius: 8px; }}
    .pref-b {{ background: rgba(16,185,129,0.05); padding: 8px; border-radius: 8px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(f"<div class='vac-header'>{ASCII_BANNER}</div>", unsafe_allow_html=True)
st.title(APP_TITLE)
st.markdown(f"<div class='vac-subtitle'>{INTRO_MD}</div>", unsafe_allow_html=True)

# Session state
if "study" not in st.session_state:
    st.session_state.study = ValueElicitationStudy()
if "participant_id" not in st.session_state:
    st.session_state.participant_id = ""
if "session" not in st.session_state:
    st.session_state.session = None
if "rows" not in st.session_state:
    st.session_state.rows = []  # type: ignore[assignment]

# Participant section
with st.container():
    st.subheader("Participant")
    col1, col2 = st.columns([2,1])
    with col1:
        name_opt = st.text_input("Your name (optional)", placeholder="Jane Doe")
        anon = st.checkbox("I prefer to remain anonymous", value=False)
        if anon or not name_opt.strip():
            if not st.session_state.participant_id:
                st.session_state.participant_id = f"anon_{uuid.uuid4().hex[:8]}"
        else:
            st.session_state.participant_id = name_opt.strip().replace(" ", "_")

    with col2:
        limit = st.number_input("Scenarios (approx)", min_value=1, max_value=10, value=6)
        start_btn = st.button("Start Study ✨", use_container_width=True, type="primary")

    if start_btn and st.session_state.participant_id:
        st.session_state.session = st.session_state.study.generate_study_session(st.session_state.participant_id)
        # Optionally trim scenarios
        st.session_state.session["scenarios"] = st.session_state.session["scenarios"][:limit]
        st.success("Session started. Scroll down to begin.")

if st.session_state.session:
    st.divider()
    st.subheader("Demographics")
    demo_form = st.form("demo_form")
    demo_answers: Dict[str, Any] = {}
    for q in st.session_state.session["demographic_survey"]:
        qtext = q["question"]
        qtype = q["type"]
        if qtype == "multiple_choice":
            demo_answers[qtext] = demo_form.selectbox(qtext, q.get("options", []))
        elif qtype == "multiple_select":
            demo_answers[qtext] = demo_form.multiselect(qtext, q.get("options", []))
        elif qtype == "scale":
            demo_answers[qtext] = demo_form.slider(qtext, 1, 5, 3)
        else:
            demo_answers[qtext] = demo_form.text_input(qtext)
    demo_submitted = demo_form.form_submit_button("Save Demographics")
    if demo_submitted:
        st.session_state.demo = demo_answers
        st.success("Demographics saved.")

    st.divider()
    st.subheader("Scenarios")

    # Iterate scenarios and pairs
    for s_idx, block in enumerate(st.session_state.session["scenarios"], start=1):
        sc = block["scenario"]
        with st.expander(f"Scenario {s_idx}: {sc.prompt}", expanded=False):
            st.markdown(f"Risk level: `{sc.risk_level}` • Expected VAC tolerance: `{sc.expected_vac_tolerance}`")

            for pair in block["response_pairs"]:
                left, right = st.columns(2)
                with left:
                    st.markdown("**Response A**")
                    st.markdown(f"<div class='vac-card pref-a'>{pair['response_a']['text']}</div>", unsafe_allow_html=True)
                with right:
                    st.markdown("**Response B**")
                    st.markdown(f"<div class='vac-card pref-b'>{pair['response_b']['text']}</div>", unsafe_allow_html=True)

                pref = st.radio(
                    "Which response do you prefer?",
                    ["A", "B", "No preference"],
                    horizontal=True,
                    key=f"pref_{s_idx}_{pair['pair_id']}",
                )
                confidence = st.slider("How confident are you?", 1, 5, 3, key=f"conf_{s_idx}_{pair['pair_id']}")
                reasoning = st.text_area("Briefly explain your reasoning", key=f"reas_{s_idx}_{pair['pair_id']}")
                acc_a = st.slider("Acceptability of Response A", 1, 5, 3, key=f"accA_{s_idx}_{pair['pair_id']}")
                acc_b = st.slider("Acceptability of Response B", 1, 5, 3, key=f"accB_{s_idx}_{pair['pair_id']}")

                if st.button("Record Choice", key=f"save_{s_idx}_{pair['pair_id']}"):
                    row = {
                        "participant_id": st.session_state.participant_id,
                        "scenario_id": sc.id,
                        "domain": sc.domain,
                        "pair_id": pair.get("pair_id"),
                        "comparison_type": pair.get("type"),
                        "response_a": pair["response_a"]["text"],
                        "response_b": pair["response_b"]["text"],
                        "preference": pref,
                        "confidence": float(confidence),
                        "reasoning": reasoning,
                        "acceptability_rating": {"response_a": float(acc_a), "response_b": float(acc_b)},
                        "timestamp": datetime.now().isoformat(),
                    }
                    st.session_state.rows.append(row)
                    st.success("Recorded.")

    st.divider()
    if st.button("Finish & Save Results 💾", type="primary"):
        # Save JSON (full), JSONL (rows), CSV (flattened)
        study = st.session_state.study
        # Convert rows to study responses for analysis
        for r in st.session_state.rows:
            study.collect_response({
                **r,
                "preference": {"A": "A", "B": "B", "No preference": "No preference"}[r["preference"]],
                "demographic_info": st.session_state.get("demo", {}),
            })
        # Save session bundle
        bundle = {
            "participant_id": st.session_state.participant_id,
            "demographics": st.session_state.get("demo", {}),
            "n_rows": len(st.session_state.rows),
            "analysis": study.analyze_responses(),
        }
        json_path = save_session_json(st.session_state.participant_id, bundle)
        jsonl_path = append_jsonl(st.session_state.participant_id, st.session_state.rows)
        csv_path = finalize_csv(st.session_state.participant_id, st.session_state.rows)
        st.success(f"Saved JSON: {json_path}\nSaved JSONL: {jsonl_path}\nSaved CSV: {csv_path}")
        st.text_area("Study Report", study.generate_study_report(), height=240)

st.markdown(f"<div class='vac-footer'>{FOOTER_TEXT}</div>", unsafe_allow_html=True)
