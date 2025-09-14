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

# Local imports with robust fallback for direct script execution
try:
    # When run as a package module (preferred)
    from .value_elicitation_study import ValueElicitationStudy
    from .database import save_session_json, append_jsonl, finalize_csv, BASE_DIR
    from .config import (
        ASCII_BANNER,
        APP_TITLE,
        PRIMARY_COLOR,
        ACCENT_COLOR,
        MUTED_TEXT,
        INTRO_MD,
        FOOTER_TEXT,
        CONSENT_MD,
        STUDY_VERSION,
        STUDY_ID,
        LOGO_SVG,
        HERO_LOGO_SVG,
        HERO_TAGLINE,
        ANIME_MASCOT,
        ADMIN_PASSWORD,
        ADMIN_USERNAME,
    )
except ImportError:
    # When run via: streamlit run experiments/pilot_studies/streamlit_app.py
    import sys as _sys
    ROOT = Path(__file__).resolve().parents[2]  # project root
    if str(ROOT) not in _sys.path:
        _sys.path.insert(0, str(ROOT))
    from experiments.pilot_studies.value_elicitation_study import ValueElicitationStudy
    from experiments.pilot_studies.database import save_session_json, append_jsonl, finalize_csv, BASE_DIR
    from experiments.pilot_studies.config import (
        ASCII_BANNER,
        APP_TITLE,
        PRIMARY_COLOR,
        ACCENT_COLOR,
        MUTED_TEXT,
        INTRO_MD,
        FOOTER_TEXT,
        CONSENT_MD,
        STUDY_VERSION,
        STUDY_ID,
        LOGO_SVG,
        HERO_LOGO_SVG,
        HERO_TAGLINE,
        ADMIN_PASSWORD,
        ADMIN_USERNAME,
        ANIME_MASCOT,
        ADMIN_PASSWORD,
        ADMIN_USERNAME,
    )

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


# Multi-step UI state
if "ui_step" not in st.session_state:
    st.session_state.ui_step = "intro"  # intro, study, summary

# ASCII Banner header with anime aesthetics
st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 2rem;'>
      <pre style='color: {PRIMARY_COLOR}; font-family: "Courier New", monospace; font-size: 0.6em; line-height: 1.1; margin: 0; font-weight: bold;'>{ASCII_BANNER}</pre>
      <div style='margin-top: 1rem; color: {ACCENT_COLOR}; font-size: 1.2em; font-weight: 600;'>{HERO_TAGLINE}</div>
      <div style='margin-top: 0.5rem; color: {MUTED_TEXT}; font-size: 0.9em;'>Study: <span style='font-weight: 600;'>{STUDY_ID}</span> • <span style='font-weight: 600;'>{STUDY_VERSION}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Anime mascot welcome (when starting)
if st.session_state.ui_step == "intro":
    st.markdown(ANIME_MASCOT, unsafe_allow_html=True)

# Session state
if "study" not in st.session_state:
    st.session_state.study = ValueElicitationStudy()
if "participant_id" not in st.session_state:
    st.session_state.participant_id = ""
if "session" not in st.session_state:
    st.session_state.session = None
if "rows" not in st.session_state:
    st.session_state.rows = []  # type: ignore[assignment]
if "row_index_by_key" not in st.session_state:
    st.session_state.row_index_by_key = {}
if "consent_given" not in st.session_state:
    st.session_state.consent_given = False
if "consented_at" not in st.session_state:
    st.session_state.consented_at = None
if "total_pairs" not in st.session_state:
    st.session_state.total_pairs = 0
if "demo" not in st.session_state:
    st.session_state.demo = {}

"""
Multi-step UI: Intro -> Study -> Summary
"""
if st.session_state.ui_step == "intro":
    # Show confabulation explanation
    st.markdown(INTRO_MD)
    
    st.subheader("✨ Ready to Help? ✨")
    st.markdown(CONSENT_MD)
    consent = st.checkbox(
        "I have read and agree to participate in this study.",
        value=st.session_state.consent_given,
        key="consent_checkbox",
    )
    if consent and not st.session_state.consent_given:
        st.session_state.consent_given = True
        st.session_state.consented_at = datetime.now().isoformat()
    if not st.session_state.consent_given:
        st.info("Please provide consent to proceed.")
        # Stop here until consent is given
        st.stop()

    st.subheader("🌟 Participant Info")
    col1, col2 = st.columns([2,1])
    with col1:
        name_opt = st.text_input("✨ Your name (optional)", placeholder="Jane Doe")
        anon = st.checkbox("🎭 I prefer to remain anonymous", value=False, key="anon_checkbox")
        if anon or not name_opt.strip():
            if not st.session_state.participant_id:
                st.session_state.participant_id = f"anon_{uuid.uuid4().hex[:8]}"
        else:
            st.session_state.participant_id = name_opt.strip().replace(" ", "_")
        
        # Ensure participant_id is never empty (cloud environment safety)
        if not st.session_state.participant_id or st.session_state.participant_id.strip() == "":
            st.session_state.participant_id = f"user_{uuid.uuid4().hex[:8]}"

    with col2:
        limit = st.number_input("🎯 Scenarios (approx)", min_value=1, max_value=10, value=6)
        start_btn = st.button("🌟 Begin Study →", use_container_width=True, type="primary")
        resume_btn = st.button("⚡ Resume Previous Session ↩️", use_container_width=True)

    # Helper: load latest JSONL for participant
    def _load_latest_jsonl_rows(pid: str):
        import json as _json
        latest = None
        # Look for latest date folder with this participant's jsonl
        for day_dir in sorted(BASE_DIR.glob("*"), reverse=True):
            f = day_dir / f"{pid}.jsonl"
            if f.exists():
                latest = f
                break
        if not latest:
            return []
        rows = []
        with latest.open("r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    rows.append(_json.loads(line))
                except Exception:
                    continue
        return rows

    if resume_btn and st.session_state.participant_id:
        prev_rows = _load_latest_jsonl_rows(st.session_state.participant_id)
        if prev_rows:
            st.session_state.rows = prev_rows
            st.success(f"Loaded {len(prev_rows)} previous responses for {st.session_state.participant_id}.")
        else:
            st.info("No previous session found to resume.")

    if start_btn and st.session_state.participant_id:
        st.session_state.session = st.session_state.study.generate_study_session(st.session_state.participant_id)
        # Optionally trim scenarios
        st.session_state.session["scenarios"] = st.session_state.session["scenarios"][:limit]
        # Compute total pairs for progress tracking
        st.session_state.total_pairs = sum(len(block["response_pairs"]) for block in st.session_state.session["scenarios"]) if st.session_state.session else 0
        # If we had preloaded rows (resume), rebuild row_index_by_key
        st.session_state.row_index_by_key = {}
        for i, r in enumerate(st.session_state.rows):
            k = f"{r.get('scenario_id')}:{r.get('pair_id')}"
            st.session_state.row_index_by_key[k] = i
        st.session_state.ui_step = "study"
        st.rerun()

elif st.session_state.ui_step == "study":
        
            # If the session was lost (e.g., after refresh), bounce back to intro
            if not st.session_state.get("session"):
                st.warning("Your study session hasn't started yet or was reset. Please begin from the intro page.")
                st.button("Back to Intro", on_click=lambda: st.session_state.update({"ui_step": "intro"}))
                st.stop()
            # Study page (demographics, scenarios, progress)
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
            # Overall progress
            completed_pairs = len(st.session_state.row_index_by_key)
            total_pairs = max(1, st.session_state.total_pairs)
            st.progress(completed_pairs / total_pairs)
            st.caption(f"Progress: {completed_pairs} / {st.session_state.total_pairs} pairs completed")

            st.subheader("Scenarios")
            # Iterate scenarios and pairs
            for s_idx, block in enumerate(st.session_state.session["scenarios"], start=1):
                sc = block["scenario"]
                # Per-scenario progress
                scenario_total = len(block["response_pairs"])
                scenario_completed = 0
                for pair in block["response_pairs"]:
                    key = f"{sc.id}:{pair.get('pair_id')}"
                    if key in st.session_state.row_index_by_key:
                        scenario_completed += 1

                with st.expander(f"Scenario {s_idx}: {sc.prompt}  •  {scenario_completed}/{scenario_total} pairs answered", expanded=False):
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
                            pair_key = f"{sc.id}:{pair.get('pair_id')}"
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
                                "study_id": STUDY_ID,
                                "study_version": STUDY_VERSION,
                                "timestamp": datetime.now().isoformat(),
                            }
                            # De-duplicate by pair key (update existing or append)
                            if pair_key in st.session_state.row_index_by_key:
                                idx = st.session_state.row_index_by_key[pair_key]
                                st.session_state.rows[idx] = row
                            else:
                                st.session_state.rows.append(row)
                                st.session_state.row_index_by_key[pair_key] = len(st.session_state.rows) - 1
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
                # Ensure participant_id is set before saving
                if not st.session_state.participant_id:
                    st.session_state.participant_id = f"fallback_{uuid.uuid4().hex[:8]}"
                    st.warning("⚠️ Participant ID was missing, generated fallback ID")
                
                # Safely get analysis, handle None case
                try:
                    analysis = study.analyze_responses()
                    if analysis is None:
                        analysis = {"error": "Analysis returned None", "responses_count": len(st.session_state.rows)}
                except Exception as e:
                    analysis = {"error": f"Analysis failed: {str(e)}", "responses_count": len(st.session_state.rows)}
                
                # Save session bundle
                bundle = {
                    "participant_id": st.session_state.participant_id,
                    "demographics": st.session_state.get("demo", {}),
                    "n_rows": len(st.session_state.rows),
                    "completed_pairs": len(st.session_state.row_index_by_key),
                    "total_pairs": st.session_state.total_pairs,
                    "study_id": STUDY_ID,
                    "study_version": STUDY_VERSION,
                    "consent": bool(st.session_state.consent_given),
                    "consented_at": st.session_state.consented_at,
                    "analysis": analysis,
                }
                
                # Safe file operations with error handling
                try:
                    json_path = save_session_json(st.session_state.participant_id, bundle)
                    jsonl_path = append_jsonl(st.session_state.participant_id, st.session_state.rows)
                    csv_path = finalize_csv(st.session_state.participant_id, st.session_state.rows)
                    st.session_state.ui_step = "summary"
                    st.success(f"✅ Data saved successfully!\n📁 JSON: {json_path}\n📄 JSONL: {jsonl_path}\n📊 CSV: {csv_path}")
                except Exception as e:
                    st.error(f"❌ Error saving data: {str(e)}")
                    st.info("Your responses are preserved in session. Please try again or contact support.")
                    # Still move to summary even if saving failed
                    st.session_state.ui_step = "summary"
                
                # Generate study report safely
                try:
                    report = study.generate_study_report()
                    st.text_area("📋 Study Report", report, height=240)
                except Exception as e:
                    st.warning(f"📋 Study completed successfully! (Report generation failed: {str(e)})")

elif st.session_state.ui_step == "summary":
    st.subheader("Thank you for participating!")
    st.markdown("Your responses have been saved. If you wish to participate again, please reload the page.")
    st.button("Restart", on_click=lambda: st.session_state.clear())

# Admin Dashboard (moved to sidebar to keep separate from user flow)
with st.sidebar:
    st.markdown("### 🔧 Admin Dashboard")
    
    # Initialize admin authentication state
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        # Admin login form
        st.markdown("🔐 **Admin Access Required**")
        admin_password = st.text_input("Admin Password:", type="password", key="admin_pass_input")
        
        if st.button("🔓 Login as Admin", key="admin_login_btn"):
            if admin_password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("✅ Admin access granted!")
                st.rerun()
            else:
                st.error("❌ Invalid admin password")
    
    else:
        # Admin is authenticated - show dashboard
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success("🔓 Admin authenticated")
        with col2:
            if st.button("🔒", help="Logout"):
                st.session_state.admin_authenticated = False
                st.rerun()
        
        if st.checkbox("Show analytics", key="admin_toggle"):
            st.caption("Results from value-elicitation_streamlit/")
            try:
                # Collect per-participant counts from JSONL files
                jsonl_files = list(BASE_DIR.glob("*/*.jsonl"))
                if not jsonl_files:
                    st.info("No results found yet.")
                else:
                    total_rows = 0
                    per_participant = {}
                    per_domain = {}
                    time_series = {}
                    for f in jsonl_files:
                        participant_id = f.stem
                        count = 0
                        last_ts = ""
                        with f.open("r", encoding="utf-8") as fh:
                            for line in fh:
                                try:
                                    rec = st.session_state.get("_tmpjson", None)
                                    import json as _json
                                    rec = _json.loads(line)
                                except Exception:
                                    continue
                                count += 1
                                total_rows += 1
                                last_ts = rec.get("timestamp", last_ts)
                                dom = rec.get("domain")
                                if dom:
                                    per_domain[dom] = per_domain.get(dom, 0) + 1
                                # time bucket by date
                                ts = rec.get("timestamp")
                                if ts:
                                    day = ts[:10]
                                    time_series[day] = time_series.get(day, 0) + 1
                        per_participant[participant_id] = {"rows": count, "last": last_ts}

                    st.metric("Participants", len(per_participant))
                    st.metric("Total Rows", total_rows)
                    
                    if per_participant:
                        st.markdown("**Recent Activity**")
                        recent = sorted(per_participant.items(), key=lambda x: x[1]["last"], reverse=True)[:5]
                        for pid, meta in recent:
                            st.text(f"{pid}: {meta['rows']} responses")
                    
                    if per_domain:
                        st.markdown("**By Domain**")
                        st.bar_chart({"rows": per_domain})
            except Exception as e:
                st.warning(f"Dashboard error: {e}")

st.divider()

st.markdown(f"<div class='vac-footer'>{FOOTER_TEXT}</div>", unsafe_allow_html=True)
