"""Config and style helpers for the Streamlit value elicitation app."""

ASCII_BANNER = ""  # Deprecated

# Modern hero header content
HERO_TAGLINE = "A research pilot to understand when AI confabulation is acceptable."
HERO_LOGO_SVG = """
<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
            <stop stop-color="#4F46E5"/>
            <stop offset="1" stop-color="#10B981"/>
        </linearGradient>
    </defs>
    <rect x="8" y="8" width="48" height="48" rx="16" fill="url(#grad)" opacity="0.13"/>
    <circle cx="32" cy="32" r="16" stroke="#4F46E5" stroke-width="3" fill="#fff"/>
    <path d="M24 32h16M32 24v16" stroke="#10B981" stroke-width="3" stroke-linecap="round"/>
    <circle cx="32" cy="32" r="4" fill="#4F46E5"/>
</svg>
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

Thank you for considering this research study. You’ll be shown short scenarios and asked to compare two possible AI responses. Your choices and ratings will help us understand when people find confabulation acceptable in AI.

Your responses are anonymous and will be used only for research. You may stop at any time. By continuing, you agree to participate.
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
