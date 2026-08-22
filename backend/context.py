from pathlib import Path

from backend.prompts import TWIN_SYSTEM_PROMPT

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"


def load_text_file(filename: str) -> str:
    path = DOCS_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return file.read().strip()


CORE_PROFILE = load_text_file("core_profile.md")
CAREER_PROFILE = load_text_file("career_profile.md")

TWIN_CONTEXT = f"""
# CORE PROFILE

{CORE_PROFILE}

# DETAILED CAREER PROFILE

{CAREER_PROFILE}
""".strip()

TWIN_INSTRUCTIONS = f"""
{TWIN_SYSTEM_PROMPT}

# INFORMATION ABOUT IGNACIO

The following information is the authoritative professional context
available to you.

{TWIN_CONTEXT}
""".strip()
