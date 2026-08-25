import json
import os
import smtplib

from backend.context import load_text_file
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

PROFILE_SECTIONS = {
    "projects": "projects.md",
    "interests": "interests.md",
    "other": "extended_profile.md",
}

# ============================================================
# TOOL TRIGGERS
# ============================================================

tool_retrieve_more_info = {
    "name": "retrieve_more_info",
    "description": (
        "Retrieve additional authoritative information about Ignacio "
        "from his extended professional profile. "
        "Use this tool ONLY when the core profile does not contain "
        "enough information to answer a question specifically about "
        "Ignacio, his background, career, projects, interests, skills, "
        "experience, or other professional/personal profile information. "
        "Choose 'projects' for questions about Ignacio's projects, "
        "'interests' for questions about Ignacio's interests, and "
        "'other' for other relevant information about Ignacio that is "
        "not covered by projects or interests. "
        "Do NOT use this tool for general knowledge, unrelated questions, "
        "or information that can be answered without knowing more about Ignacio."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "section": {
                "type": "string",
                "description": "The profile section to retrieve.",
                "enum": [
                    "projects",
                    "interests",
                    "other",
                ],
            }
        },
        "required": ["section"],
        "additionalProperties": False,
    },
}

tool_email = {
    "name": "record_email",
    "description": "Send an email to a specified recipient.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "The email address of the recipient",
            },
            "subject": {
                "type": "string",
                "description": "The subject of the email",
            },
            "body": {
                "type": "string",
                "description": "The content of the email",
            },
        },
        "required": ["to", "subject", "body"],
        "additionalProperties": False,
    },
}

# ============================================================
# TOOL FUNCTIONS
# ============================================================

def record_email(to: str, subject: str, body: str):
    sender = EMAIL_USER
    password = EMAIL_PASSWORD

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    return "OK"

def retrieve_more_info(section: str) -> str:
    filename = PROFILE_SECTIONS.get(section)

    if not filename:
        return f"Unknown profile section: {section}"

    return load_text_file(filename)

tool_map = {
    "retrieve_more_info": retrieve_more_info,
    "record_email": record_email,
}

# ============================================================
# TOOL CALL HANDLER
# ============================================================

def handle_tool_calls(tool_calls):
    results = []

    for tool_call in tool_calls:
        tool_name = tool_call.name
        arguments = json.loads(tool_call.arguments)

        tool = tool_map.get(tool_name)

        result = tool(**arguments) if tool else "No tool found"

        results.append(
            {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(result),
            }
        )

    return results

tools = [
    {
        "type": "function",
        "name": tool_email["name"],
        "description": tool_email["description"],
        "parameters": tool_email["parameters"],
    },
    {
        "type": "function",
        "name": tool_retrieve_more_info["name"],
        "description": tool_retrieve_more_info["description"],
        "parameters": tool_retrieve_more_info["parameters"],
    },
]