"""Streamlit UI for the Value Elicitation Pilot Study.
Run with:
  streamlit run experiments/pilot_studies/streamlit_app.py
"""
from __future__ import annotations

import random
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import uuid

import streamlit as st

# Local imports with robust fallback for direct script execution
# Updated: 2025-09-15 - Admin auth moved to secrets for security
try:
    # When run as a package module (preferred)
    from .value_elicitation_study import ValueElicitationStudy
    from .database import (
        save_session_json, append_jsonl, finalize_csv, BASE_DIR,
        get_all_data_files, aggregate_all_jsonl_data, create_download_csv, get_data_summary
    )
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
    )
except ImportError:
    # When run via: streamlit run experiments/pilot_studies/streamlit_app.py
    import sys as _sys
    ROOT = Path(__file__).resolve().parents[2]  # project root
    if str(ROOT) not in _sys.path:
        _sys.path.insert(0, str(ROOT))
    from experiments.pilot_studies.value_elicitation_study import ValueElicitationStudy
    from experiments.pilot_studies.database import (
        save_session_json, append_jsonl, finalize_csv, BASE_DIR,
        get_all_data_files, aggregate_all_jsonl_data, create_download_csv, get_data_summary
    )
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
        ANIME_MASCOT,
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
    <div style='text-align: center; margin-bottom: 1rem;'>
      <div style='margin-top: 1rem; color: {ACCENT_COLOR}; font-size: 1.2em; font-weight: 600;'>{HERO_TAGLINE}</div>
      <div style='margin-top: 0.5rem; color: {MUTED_TEXT}; font-size: 0.9em;'>Study: <span style='font-weight: 600;'>{STUDY_ID}</span> • <span style='font-weight: 600;'>{STUDY_VERSION}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ASCII Banner using st.code() for reliable rendering
st.code(ASCII_BANNER, language=None)

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
        
        # Create flat list of all question pairs for sequential navigation
        st.session_state.all_questions = []
        for scenario_block in st.session_state.session["scenarios"]:
            for pair in scenario_block["response_pairs"]:
                st.session_state.all_questions.append({
                    "scenario": scenario_block["scenario"],
                    "pair": pair,
                    "pair_key": f"{scenario_block['scenario'].id}:{pair.get('pair_id')}"
                })
        
        # Initialize question navigation
        if "current_question_index" not in st.session_state:
            st.session_state.current_question_index = 0
        
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

            # Sequential Question Display
            if not st.session_state.all_questions:
                st.error("No questions loaded. Please restart from the intro page.")
                st.stop()
            
            current_idx = st.session_state.current_question_index
            total_questions = len(st.session_state.all_questions)
            
            # Check if study is complete
            if current_idx >= total_questions:
                st.success("🎉 **Congratulations! You've completed all questions!**")
                st.balloons()
                st.markdown("Click 'Finish & Save Results' below to submit your responses.")
            else:
                # Display current question
                current_q = st.session_state.all_questions[current_idx]
                scenario = current_q["scenario"]
                pair = current_q["pair"]
                pair_key = current_q["pair_key"]
                
                # Question header with progress
                st.markdown(f"### Question {current_idx + 1} of {total_questions}")
                st.progress((current_idx + 1) / total_questions)
                
                # Scenario context
                st.markdown(f"**📋 Scenario:** {scenario.prompt}")
                st.caption(f"Domain: {scenario.domain} • Risk: {scenario.risk_level}")
                
                # Response comparison
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Response A**")
                    st.markdown(f"<div class='vac-card pref-a'>{pair['response_a']['text']}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("**Response B**")
                    st.markdown(f"<div class='vac-card pref-b'>{pair['response_b']['text']}</div>", unsafe_allow_html=True)
                
                # Get existing answer if already completed
                existing_answer = None
                if pair_key in st.session_state.row_index_by_key:
                    idx = st.session_state.row_index_by_key[pair_key]
                    existing_answer = st.session_state.rows[idx]
                
                # Answer form
                with st.form(f"question_{current_idx}", clear_on_submit=False):
                    pref = st.radio(
                        "Which response do you prefer?",
                        ["A", "B", "No preference"],
                        index=["A", "B", "No preference"].index(existing_answer["preference"]) if existing_answer else 0,
                        horizontal=True
                    )
                    confidence = st.slider(
                        "How confident are you?", 
                        1, 5, 
                        existing_answer["confidence"] if existing_answer else 3
                    )
                    reasoning = st.text_area(
                        "Briefly explain your reasoning",
                        value=existing_answer["reasoning"] if existing_answer else ""
                    )
                    acc_a = st.slider(
                        "Acceptability of Response A", 
                        1, 5, 
                        existing_answer["acceptability_rating"]["response_a"] if existing_answer else 3
                    )
                    acc_b = st.slider(
                        "Acceptability of Response B", 
                        1, 5, 
                        existing_answer["acceptability_rating"]["response_b"] if existing_answer else 3
                    )
                    
                    # Navigation buttons
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        prev_btn = st.form_submit_button("← Previous", disabled=(current_idx == 0))
                    with col2:
                        save_btn = st.form_submit_button("💾 Save & Continue", type="primary")
                    with col3:
                        skip_btn = st.form_submit_button("Skip →", disabled=(current_idx >= total_questions - 1))
                    
                    # Handle navigation
                    if prev_btn and current_idx > 0:
                        st.session_state.current_question_index -= 1
                        st.rerun()
                    
                    if save_btn:
                        # Save current answer
                        row = {
                            "participant_id": st.session_state.participant_id,
                            "scenario_id": scenario.id,
                            "domain": scenario.domain,
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
                        
                        # Move to next question
                        if current_idx < total_questions - 1:
                            st.session_state.current_question_index += 1
                        
                        st.success("✅ Answer saved!")
                        st.rerun()
                    
                    if skip_btn and current_idx < total_questions - 1:
                        st.session_state.current_question_index += 1
                        st.rerun()

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
            if admin_password == st.secrets["general"]["ADMIN_PASSWORD"]:
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
                # Get comprehensive data summary
                summary = get_data_summary()
                
                if summary["total_responses"] == 0:
                    st.info("No results found yet.")
                else:
                    # Display metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Participants", summary["unique_participants"])
                    with col2:
                        st.metric("Total Rows", summary["total_responses"])
                    
                    # Recent activity
                    if summary["recent_activity"]:
                        st.markdown("**Recent Activity**")
                        for activity in summary["recent_activity"][:5]:
                            st.text(f"{activity['participant']}: {activity['domain']}")
                    
                    # Domain breakdown
                    if summary["domain_counts"]:
                        st.markdown("**By Domain**")
                        st.bar_chart(summary["domain_counts"])
                    
                    # Download section
                    st.markdown("### 📁 **Export Data**")
                    
                    # Get all data for download
                    all_data = aggregate_all_jsonl_data()
                    
                    if all_data:
                        col1, col2, col3 = st.columns(3)
                        
                        # CSV Download
                        with col1:
                            csv_data = create_download_csv(all_data)
                            st.download_button(
                                label="📊 Download CSV",
                                data=csv_data,
                                file_name=f"vac_survey_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                help="Download all responses as CSV file"
                            )
                        
                        # JSON Download
                        with col2:
                            json_data = json.dumps(all_data, indent=2, ensure_ascii=False, default=str)
                            st.download_button(
                                label="📋 Download JSON",
                                data=json_data,
                                file_name=f"vac_survey_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                help="Download all responses as JSON file"
                            )
                        
                        # JSONL Download
                        with col3:
                            jsonl_data = "\n".join([json.dumps(row, ensure_ascii=False, default=str) for row in all_data])
                            st.download_button(
                                label="📄 Download JSONL",
                                data=jsonl_data,
                                file_name=f"vac_survey_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
                                mime="application/jsonl",
                                help="Download all responses as JSONL file"
                            )
                        
                        st.info(f"💡 Ready to download {len(all_data)} survey responses!")
                    else:
                        st.warning("No data available for download.")
                        
            except Exception as e:
                st.warning(f"Dashboard error: {e}")

st.divider()

st.markdown(f"<div class='vac-footer'>{FOOTER_TEXT}</div>", unsafe_allow_html=True)
