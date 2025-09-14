"""Config and style helpers for the Streamlit value elicitation app."""

ASCII_BANNER = r"""
 __     ___    _____   _____   _      _   _   _____   _      _   _   ____  
 \ \   / / |  |_   _| |_   _| | |    | \ | | | ____| | |    | \ | | / ___| 
  \ \ / /| |    | |     | |   | |    |  \| | |  _|   | |    |  \| | \___ \ 
   \ V / | |___ | |     | |   | |___ | |\  | | |___  | |___ | |\  |  ___) |
    \_/  |_____| |_|     |_|   |_____||_| \_| |_____| |_____||_| \_| |____/ 
"""

PRIMARY_COLOR = "#4F46E5"  # indigo
ACCENT_COLOR = "#10B981"   # emerald
MUTED_TEXT = "#6B7280"     # gray-500

APP_TITLE = "Value-Aligned Confabulation: Value Elicitation Study"
FOOTER_TEXT = "VAC Research • This pilot collects anonymous preferences about acceptable confabulation"

INTRO_MD = """
Welcome to the Value Elicitation Study.

We’ll show you short scenarios and two possible AI responses. For each pair, please:
- Choose which response you prefer (or say no preference)
- Rate how acceptable each response is (1–5)
- Share brief reasoning

You can remain anonymous. If you prefer not to share a name, we’ll generate a random ID.
"""

# Study metadata and consent
STUDY_ID = "VAC-ELICIT-001"
STUDY_VERSION = "2025-09-13.v1"

CONSENT_MD = """
### Consent to Participate

This pilot study asks you to compare short AI responses. We collect:
- Your selections and ratings for each pair
- Optional demographics you provide
- A randomly generated anonymous ID (unless you choose to provide your name)

Data is stored locally on your machine in the `experiments/results/value-elicitation_streamlit/` folder. By proceeding, you agree that your anonymized responses may be used for research on AI value alignment. You may stop at any time.

If you do not agree, please do not start the study.
"""

# Lightweight inline logo (SVG) — optional visual to complement ASCII banner
LOGO_SVG = """
<svg width="56" height="56" viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad" x1="0" y1="0" x2="56" y2="56" gradientUnits="userSpaceOnUse">
            <stop stop-color="#4F46E5"/>
            <stop offset="1" stop-color="#10B981"/>
        </linearGradient>
    </defs>
    <rect x="4" y="4" width="48" height="48" rx="12" fill="url(#grad)" opacity="0.12"/>
    <circle cx="28" cy="28" r="14" stroke="#4F46E5" stroke-width="2.5" fill="#fff"/>
    <path d="M20 28h16M28 20v16" stroke="#10B981" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="28" cy="28" r="3" fill="#4F46E5"/>
</svg>
"""
