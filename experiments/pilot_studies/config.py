"""Config and style helpers for the Streamlit value elicitation app."""

# ASCII Banner for header
ASCII_BANNER = r"""
██╗   ██╗ █████╗  ██████╗    ██████╗ ███████╗███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
██║   ██║██╔══██╗██╔════╝    ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
██║   ██║███████║██║         ██████╔╝█████╗  ███████╗█████╗  ███████║██████╔╝██║     ███████║
╚██╗ ██╔╝██╔══██║██║         ██╔══██╗██╔══╝  ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
 ╚████╔╝ ██║  ██║╚██████╗    ██║  ██║███████╗███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
"""

# Anime-style mascot and aesthetics
HERO_TAGLINE = "🌸 Help us understand when AI creativity is helpful vs harmful! 🌸"
ANIME_MASCOT = """
<div style="text-align: center; margin: 30px 0; padding: 20px; background: linear-gradient(135deg, #FFE1E6, #E0F3FF); border-radius: 20px; border: 3px solid #FF69B4;">
  <div style="font-size: 5em; margin-bottom: 15px; animation: bounce 2s infinite;">🤖✨</div>
  <div style="font-size: 1.4em; color: #FF69B4; font-weight: bold; margin-bottom: 10px;">AI-chan needs your wisdom!</div>
  <div style="font-size: 1em; color: #6B7280;">Help me learn when creativity is good vs bad! (◕‿◕)✨</div>
  <div style="font-size: 2em; margin-top: 10px;">💖 🌟 💫</div>
</div>
<style>
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}
</style>
"""

# Additional kawaii elements for the UI
SPARKLES = "✨ 🌟 💫 ⭐"
CUTE_EMOJIS = "🌸 🌺 🦋 🌈 💕 💖 🎀"

# Kawaii color scheme
PRIMARY_COLOR = "#FF69B4"  # kawaii pink
ACCENT_COLOR = "#87CEEB"   # sky blue  
MUTED_TEXT = "#6B7280"     # gray-500

APP_TITLE = "🌟 Value-Aligned Confabulation Study 🌟"
FOOTER_TEXT = "Made with 💖 by VAC Research • Help AI learn when creativity is helpful!"

# Friendly introduction with confabulation definition
INTRO_MD = """
## What is Confabulation? 🤔

**Confabulation** is when AI creates responses that aren't strictly factual but might still be helpful or creative. Think of it like:

- 🎨 **Creative Confabulation**: AI writes an inspiring story when you're sad
- 🚫 **Harmful Confabulation**: AI gives wrong medical advice  
- ✅ **Helpful Confabulation**: AI encourages you even if it can't verify every detail

### Your Mission 🎯
Compare AI responses and tell us which ones you prefer! Your choices help us understand when AI creativity is acceptable vs when strict accuracy matters most.

*This is anonymous and takes about 10 minutes.* ⏱️
"""

# Study metadata and consent
STUDY_ID = "VAC-ELICIT-001"
STUDY_VERSION = "2025-09-13.v1"

# Simple, friendly consent (no technical jargon)
CONSENT_MD = """
### Ready to Help? 🤝

We're studying when AI creativity is helpful vs harmful. You'll see scenarios and pick which AI response you prefer.

**What we collect:** Your anonymous choices and ratings  
**Time needed:** About 10 minutes  
**Your choice:** You can stop anytime  

By clicking "I agree" below, you're saying it's okay for us to use your anonymous responses for research.
"""

# Lightweight inline logo (SVG) — optional visual to complement ASCII banner
LOGO_SVG = """
<svg width="56" height="56" viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="56" y2="56" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FF69B4"/>
      <stop offset="1" stop-color="#87CEEB"/>
    </linearGradient>
  </defs>
  <rect x="4" y="4" width="48" height="48" rx="12" fill="url(#grad)" opacity="0.12"/>
  <circle cx="28" cy="28" r="14" stroke="#FF69B4" stroke-width="2.5" fill="#fff"/>
  <path d="M20 28h16M28 20v16" stroke="#87CEEB" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="28" cy="28" r="3" fill="#FF69B4"/>
</svg>
"""

# For backward compatibility with existing imports
HERO_LOGO_SVG = LOGO_SVG